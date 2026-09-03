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
limit=""

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
  my @full_shots = $block =~ /【镜头(\d{2})｜[^｜】\n]+｜[^｜】\n]+｜[^】\n]+】/g;
  if (!@shots) {
    push @errors, 'missing numbered shot header';
  } else {
    for my $shot_index (0 .. $#shots) {
      my $expected = sprintf '%02d', $shot_index + 1;
      push @errors, "shot sequence expected=$expected actual=$shots[$shot_index]"
        unless $shots[$shot_index] eq $expected;
    }
    push @errors, 'shot header must include shot size, camera/viewpoint, and camera path/transition; complex headers may append composition and rhythm summaries'
      unless @full_shots == @shots;
  }

  while ($block =~ /(【镜头\d{2}｜[^】\n]+】)(.*?)(?=【镜头\d{2}｜|\z)/sg) {
    my ($header, $shot_body) = ($1, $2);
    my $visible = $shot_body =~ /(?:先看见|画面|镜头|前景|中景|后景|焦平面|构图|主体|人物|孩子|男人|女人|女生|男生|师兄|师妹)/;
    my $change = $shot_body =~ /(?:听到|说完|随后|然后|同时|当[^，。；\n]{0,30}时|开始|触发|才|转为|移向|抬起|落下|停住|变化)/;
    my $endpoint = $shot_body =~ /(?:最后|最终|停在|停住|锁住|保持|结束|交给|定格|余响|余韵|落回|退入|出画|切入)/;
    push @errors, "$header missing visible starting evidence" unless $visible;
    push @errors, "$header missing triggered screen/sound change" unless $change;
    push @errors, "$header missing visible/audible endpoint" unless $endpoint;
  }

  if ($block =~ /(?:片内\s*)?\d+(?:\.\d+)?\s*[—–-]\s*\d+(?:\.\d+)?\s*秒/) {
    push @errors, 'absolute second range found';
  }

  if ($block =~ /(?:不生成|不使用|不新增|不要出现|避免出现|禁止生成)/) {
    push @errors, 'direct negative generation instruction found';
  }

  if ($block =~ /(?:让观众|观众(?:看见|看到|感到|理解|知道|得到)|为了表现|为了说明|戏剧任务|表演任务|人物调度目标|这一镜(?:证明|表达|说明)|形成[^。；\n]{0,40}受控变化)/) {
    push @errors, 'author explanation found';
  }

  if ($block =~ /不是[^。；\n]{0,48}而是/) {
    push @errors, 'contrastive author explanation found';
  }

  if ($block =~ /(?:焦点[^。；\n]{0,24}抬到|抬焦|跟焦到(?:情绪|眼神)|焦点扫向)/) {
    push @errors, 'ambiguous focus/camera movement phrase found';
  }

  if ($block =~ /【(?:台词|对白)(?:-[^】]+)?】/) {
    push @errors, 'detached dialogue rail found; dialogue must be embedded in shot prose';
  }

  if ($block =~ /(?<![A-Za-z0-9])F\d+(?!\d)/) {
    push @errors, 'F portrait reference is a B-only production intermediate and cannot enter video prompts';
  }

  my $chars = length $block;
  my $shown_limit = defined $limit && length $limit ? $limit : 'none';
  push @errors, "chars=$chars exceeds limit=$limit"
    if defined $limit && length $limit && $chars > $limit;

  my $status = @errors ? 'FAIL' : 'PASS';
  printf "block=%d chars=%d limit=%s shots=%d status=%s", $index + 1, $chars, $shown_limit, scalar @shots, $status;
  printf " errors=%s", join('; ', @errors) if @errors;
  printf "\n";
  $failed = 1 if @errors;
}

exit $failed ? 1 : 0;
PERL
