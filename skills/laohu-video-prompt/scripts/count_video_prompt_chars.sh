#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <markdown-file> [--limit N] [--block N]\n' "$(basename "$0")" >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

file="$1"
shift
limit=""
block=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      limit="$2"
      shift 2
      ;;
    --block)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      block="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

[[ -f "$file" ]] || { printf 'File not found: %s\n' "$file" >&2; exit 2; }

perl -MEncode=decode -MEncode=FB_CROAK - "$file" "$limit" "$block" <<'PERL'
use strict;
use warnings;
use utf8;

my ($path, $limit, $requested_block) = @ARGV;
open my $handle, '<:raw', $path or die "Cannot read $path: $!\n";
local $/;
my $raw = <$handle>;
close $handle;
my $text = decode('UTF-8', $raw, FB_CROAK);
my @lines = split /\n/, $text, -1;
my @prompt_blocks;
my $inside = 0;
my @body;

for my $line (@lines) {
  $line =~ s/\r\z//;
  if (!$inside && $line =~ /^```/) {
    $inside = 1;
    @body = ();
    next;
  }
  if ($inside && $line =~ /^```\s*$/) {
    my $candidate = join "\n", @body;
    if ($candidate =~ /【基础设定】/ &&
        $candidate =~ /【场景状态与氛围画质】/ &&
        $candidate =~ /【画面内容】/) {
      push @prompt_blocks, $candidate;
    }
    $inside = 0;
    @body = ();
    next;
  }
  push @body, $line if $inside;
}

die "No formal video prompt text block found: $path\n" unless @prompt_blocks;
die "Unclosed code block found: $path\n" if $inside;

my @selected_indices = (0 .. $#prompt_blocks);
if (defined $requested_block && length $requested_block) {
  my $index = $requested_block - 1;
  die "Requested prompt block does not exist: $requested_block\n"
    if $index < 0 || $index >= @prompt_blocks;
  @selected_indices = ($index);
}

my $failed = 0;
for my $index (@selected_indices) {
  my $chars = length $prompt_blocks[$index];
  my $status = 'INFO';
  my $shown_limit = 'none';
  if (defined $limit && length $limit) {
    $shown_limit = $limit;
    $status = $chars <= $limit ? 'PASS' : 'FAIL';
    $failed = 1 if $status eq 'FAIL';
  }
  printf "block=%d chars=%d limit=%s status=%s\n", $index + 1, $chars, $shown_limit, $status;
}

exit $failed ? 1 : 0;
PERL
