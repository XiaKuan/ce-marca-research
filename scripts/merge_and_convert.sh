#!/bin/bash
# 合并论文章节并转换为 PDF
# 使用方法：./scripts/merge_and_convert.sh

set -e

echo "=========================================="
echo "📄 CE-MARCA 论文合并与转换脚本"
echo "=========================================="

# 设置目录
PAPER_DIR="paper"
OUTPUT_DIR="output"
TEMP_FILE="${OUTPUT_DIR}/merged.md"

# 创建输出目录
mkdir -p ${OUTPUT_DIR}

echo ""
echo "[1/4] 合并论文章节..."

# 创建合并文件
cat ${PAPER_DIR}/00-title-page.md > ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/01-introduction-polished.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/02-related-work-polished.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/03-methodology-polished.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/04-evaluation-polished.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/05-case-study-polished.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/06-discussion-polished.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/07-conclusion-polished.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/08-appendix.md >> ${TEMP_FILE}
echo "" >> ${TEMP_FILE}
cat ${PAPER_DIR}/references.md >> ${TEMP_FILE}

echo "✅ 合并完成：${TEMP_FILE}"

# 统计字数
WORD_COUNT=$(wc -w < ${TEMP_FILE})
CHAR_COUNT=$(wc -m < ${TEMP_FILE})
LINE_COUNT=$(wc -l < ${TEMP_FILE})

echo ""
echo "[2/4] 文档统计:"
echo "  - 行数：${LINE_COUNT}"
echo "  - 单词数：${WORD_COUNT}"
echo "  - 字符数：${CHAR_COUNT}"

echo ""
echo "[3/4] 转换为 PDF..."

# 使用 pandoc 转换为 PDF
pandoc ${TEMP_FILE} \
  --output=${OUTPUT_DIR}/ce-marca-paper.pdf \
  --from=markdown \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --pdf-engine=xelatex \
  --variable documentclass=article \
  --variable classoption=oneside \
  --variable geometry:margin=1in \
  --variable mainfont="DejaVu Sans" \
  --variable CJKmainfont="WenQuanYi Micro Hei" \
  2>&1 || echo "⚠️  PDF 转换需要 LaTeX 支持，尝试使用 HTML 作为备选..."

# 如果 PDF 转换失败，生成 HTML
if [ ! -f ${OUTPUT_DIR}/ce-marca-paper.pdf ]; then
  echo ""
  echo "[备选] 转换为 HTML..."
  pandoc ${TEMP_FILE} \
    --output=${OUTPUT_DIR}/ce-marca-paper.html \
    --from=markdown \
    --toc \
    --toc-depth=3 \
    --number-sections \
    --standalone \
    --css https://cdn.jsdelivr.net/npm/github-markdown-css@5.2.0/github-markdown.min.css \
    --variable title="CE-MARCA Paper"
  
  echo "✅ HTML 生成完成：${OUTPUT_DIR}/ce-marca-paper.html"
fi

echo ""
echo "[4/4] 生成其他格式..."

# 生成 Word 文档
pandoc ${TEMP_FILE} \
  --output=${OUTPUT_DIR}/ce-marca-paper.docx \
  --from=markdown \
  --toc \
  --toc-depth=2

echo "✅ Word 文档生成完成：${OUTPUT_DIR}/ce-marca-paper.docx"

# 生成 LaTeX 源码
pandoc ${TEMP_FILE} \
  --output=${OUTPUT_DIR}/ce-marca-paper.tex \
  --from=markdown \
  --toc \
  --number-sections

echo "✅ LaTeX 源码生成完成：${OUTPUT_DIR}/ce-marca-paper.tex"

echo ""
echo "=========================================="
echo "✅ 所有转换完成！"
echo "=========================================="
echo ""
echo "输出文件:"
ls -lh ${OUTPUT_DIR}/

echo ""
echo "查看 PDF（如果已生成）:"
echo "  evince ${OUTPUT_DIR}/ce-marca-paper.pdf &"
echo ""
echo "查看 HTML:"
echo "  firefox ${OUTPUT_DIR}/ce-marca-paper.html &"
echo ""
