#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'Usage: %s <markdown-file> [--limit N]\n' "$(basename "$0")" >&2
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

file="$1"
shift
limit="10000"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)
      [[ $# -ge 2 && "$2" =~ ^[1-9][0-9]*$ ]] || { usage; exit 2; }
      limit="$2"
      shift 2
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

[[ -f "$file" ]] || { printf 'File not found: %s\n' "$file" >&2; exit 2; }

perl -MEncode=decode -MEncode=FB_CROAK - "$file" "$limit" <<'PERL'
use strict;
use warnings;
use utf8;

my ($path, $limit) = @ARGV;
open my $handle, '<:raw', $path or die "Cannot read $path: $!\n";
local $/;
my $raw = <$handle>;
close $handle;
my $text = decode('UTF-8', $raw, FB_CROAK);
my @lines = split /\n/, $text, -1;
my @blocks;
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
    if ($candidate =~ /【基础设定】/ ||
        $candidate =~ /【场景状态与氛围画质】/ ||
        $candidate =~ /【画面内容】/) {
      push @blocks, $candidate;
    }
    $inside = 0;
    @body = ();
    next;
  }
  push @body, $line if $inside;
}

die "Unclosed code block found: $path\n" if $inside;
die "No video prompt text block found: $path\n" unless @blocks;

my $failed = 0;
for my $index (0 .. $#blocks) {
  my $block = $blocks[$index];
  my @errors;

  for my $heading ('【基础设定】', '【场景状态与氛围画质】', '【画面内容】') {
    my $count = () = $block =~ /\Q$heading\E/g;
    push @errors, "$heading count=$count" unless $count == 1;
  }

  my @shots = $block =~ /【镜头(\d{2})｜/g;
  if (!@shots) {
    push @errors, 'missing numbered shot header';
  } else {
    for my $shot_index (0 .. $#shots) {
      my $expected = sprintf '%02d', $shot_index + 1;
      push @errors, "shot sequence expected=$expected actual=$shots[$shot_index]"
        unless $shots[$shot_index] eq $expected;
    }
  }

  if ($block =~ /(?:片内\s*)?\d+(?:\.\d+)?\s*[—–-]\s*\d+(?:\.\d+)?\s*秒/) {
    push @errors, 'absolute second range found';
  }

  if ($block =~ /(?:不生成|不使用|不新增|不要出现|避免出现|禁止生成)/) {
    push @errors, 'direct negative generation instruction found';
  }

  if ($block =~ /(?:让观众|为了表现|为了说明|形成[^。；\n]{0,40}受控变化)/) {
    push @errors, 'author explanation found';
  }

  my $chars = length $block;
  push @errors, "chars=$chars exceeds limit=$limit" if $chars > $limit;

  my $status = @errors ? 'FAIL' : 'PASS';
  printf "block=%d chars=%d limit=%d shots=%d status=%s", $index + 1, $chars, $limit, scalar @shots, $status;
  printf " errors=%s", join('; ', @errors) if @errors;
  printf "\n";
  $failed = 1 if @errors;
}

exit $failed ? 1 : 0;
PERL
