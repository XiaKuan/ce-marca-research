# 📄 论文格式转换说明

**转换时间**：2026-03-19 13:54

**合并后的论文**：`output/merged.md`

---

## ✅ 已生成的格式

### 1. HTML 格式（推荐查看）
**文件**：`output/ce-marca-paper.html` (113 KB)

**特点**：
- ✅ 包含完整目录
- ✅ 支持数学公式（MathJax 渲染）
- ✅ 可直接在浏览器中查看
- ✅ 支持链接跳转

**查看方式**：
```bash
# 在浏览器中打开
firefox output/ce-marca-paper.html

# 或使用其他浏览器
google-chrome output/ce-marca-paper.html
```

### 2. Word 文档
**文件**：`output/ce-marca-paper.docx` (44 KB)

**特点**：
- ✅ 可编辑
- ✅ 适合投稿前修改
- ✅ 保留章节结构

**查看方式**：
```bash
# 使用 LibreOffice
libreoffice output/ce-marca-paper.docx

# 或使用 Microsoft Word
```

### 3. LaTeX 源码
**文件**：`output/ce-marca-paper.tex` (86 KB)

**特点**：
- ✅ 适合学术投稿
- ✅ 可进一步定制格式
- ✅ 需要 LaTeX 环境编译

**编译为 PDF**：
```bash
# 使用 pdflatex
pdflatex output/ce-marca-paper.tex
pdflatex output/ce-marca-paper.tex  # 需要编译两次以生成目录

# 或使用 xelatex（支持中文）
xelatex output/ce-marca-paper.tex
xelatex output/ce-marca-paper.tex
```

### 4. Markdown 源码
**文件**：`output/merged.md` (64 KB)

**特点**：
- ✅ 原始合并文件
- ✅ 易于编辑和版本控制
- ✅ 可转换为其他格式

---

## 📊 文档统计

| 指标 | 数值 |
|------|------|
| **行数** | 1,429 |
| **单词数** | 8,240 |
| **字符数** | 61,101 |
| **章节数** | 8 + 参考文献 + 附录 |
| **估计页数** | ~25-30 页（A4, 12pt） |

---

## 📝 论文章节

1. **Title Page** - 标题页（中英文摘要）
2. **Introduction** - 引言
3. **Related Work** - 相关工作
4. **Methodology** - 方法设计
5. **Evaluation** - 实验评估
6. **Case Study** - 案例研究
7. **Discussion** - 讨论与局限
8. **Conclusion** - 结论
9. **Appendix** - 附录
10. **References** - 参考文献（50 篇）

---

## 🔧 生成 PDF 的方法

### 方法 1：使用在线转换服务

**Pandoc Online**:
1. 访问：https://pandoc.org/try/
2. 上传 `output/merged.md`
3. 选择输出格式：PDF
4. 下载生成的 PDF

**Overleaf**:
1. 访问：https://www.overleaf.com/
2. 创建新项目
3. 上传 `output/ce-marca-paper.tex`
4. 编译生成 PDF

### 方法 2：本地安装 LaTeX

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra
cd output
xelatex ce-marca-paper.tex
xelatex ce-marca-paper.tex
```

**macOS**:
```bash
# 安装 MacTeX
brew install --cask mactex

# 编译
cd output
xelatex ce-marca-paper.tex
xelatex ce-marca-paper.tex
```

**Windows**:
1. 下载 MiKTeX: https://miktex.org/download
2. 安装后使用 `xelatex` 命令编译

### 方法 3：使用 Word 导出 PDF

```bash
# 如果有 LibreOffice
libreoffice --headless --convert-to pdf output/ce-marca-paper.docx

# 或在 Word 中打开后另存为 PDF
```

---

## 📋 投稿准备清单

### 会议/期刊投稿

**ICSE 2026**:
- [ ] PDF 格式（使用会议模板）
- [ ] 匿名版本（去除作者信息）
- [ ] 补充材料（代码仓库链接）
- [ ] 封面信

**KDD 2026**:
- [ ] PDF 格式
- [ ] 参考文献格式调整
- [ ] 图表单独上传

**IEEE TSE**:
- [ ] LaTeX 格式（使用 IEEE 模板）
- [ ] Word 文档
- [ ] 生物信息

### 预印本发布

**arXiv**:
- [ ] PDF（符合 arXiv 要求）
- [ ] 源代码（.tex 文件）
- [ ] 摘要和关键词
- [ ] 作者信息

**GitHub**:
- [ ] README 中添加论文链接
- [ ] 添加引用信息（BibTeX）

---

## 📖 引用格式

**BibTeX**:
```bibtex
@article{xia2026cemarca,
  title={CE-MARCA: Causal-Enhanced Multi-Agent Root Cause Analysis for Microservices},
  author={Xia, Kuan and Research Assistant},
  journal={arXiv preprint},
  year={2026},
  url={https://github.com/XiaKuan/ce-marca-research}
}
```

**APA 格式**:
```
Xia, K., & Research Assistant. (2026). CE-MARCA: Causal-Enhanced Multi-Agent 
Root Cause Analysis for Microservices. arXiv preprint.
```

---

## 🎯 下一步

1. **查看 HTML 版本**：
   ```bash
   firefox output/ce-marca-paper.html
   ```

2. **检查格式**：
   - 目录是否正确
   - 章节编号是否连续
   - 图表引用是否正确
   - 参考文献格式是否统一

3. **准备投稿**：
   - 选择目标会议/期刊
   - 使用官方模板重新格式化
   - 准备补充材料

4. **发布预印本**：
   - 上传到 arXiv
   - 在 GitHub README 中添加引用

---

**创建时间**：2026-03-19 13:54  
**项目**：CE-MARCA Research  
**输出目录**：`output/`
