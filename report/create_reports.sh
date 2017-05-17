#!/bin/sh
cd report
pandoc -f markdown+tex_math_single_backslash -o research_report.pdf research_review.md
pandoc -f markdown+tex_math_single_backslash -o heuristics_analysis.pdf heuristic_analysis.md 
mv *.pdf ../.
cd -
