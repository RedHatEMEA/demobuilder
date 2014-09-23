#!/bin/bash -e

for i in docs/*.md; do
  markdown2 -x fenced-code-blocks "$i" >"$(echo $i | sed -e 's/\.[^.]*$//').html"
done
