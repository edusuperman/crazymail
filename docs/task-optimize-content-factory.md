优化内容工厂脚本 tools/content_factory.py

问题：上次运行 human_markers=1 需要>=2，字数1229 需要>=1500。

需要修改3处：

1. Stage 2 的 stage2_draft 函数的 system prompt：
   - 在 Style rules 中增加：You MUST write at least 1500 words. Short articles are unacceptable.
   - 把 Short paragraphs: 3-5 sentences, under 100 words 改为 Short paragraphs: 3-5 sentences
   - 增加：Include at least 2 personal experiences or opinions using phrases like: honestly, in my testing, I have found, here is the thing, let me break this down

2. Stage 3 的 stage3_humanize 函数的 system prompt：
   - 把 Add conversational markers 改为更具体的要求：
   You MUST include at least 3 DIFFERENT human markers scattered naturally throughout the article. Use markers like: honestly, I have tested this, here is the thing, let me break this down, in my experience, the bottom line, I have seen this happen, that said, the truth is
   - 增加：These markers must appear in DIFFERENT sections of the article, not clustered together.

3. Stage 4 的 stage4_qc 函数的 human_markers 列表：
   - 增加更多匹配模式，全部小写：
   "the bottom line", "i have seen", "that said", "the truth is",
   "i have found", "in my testing", "let me break this down",
   "here is the thing", "i have tested", "who cares"

测试：修改完成后运行 python tools/content_factory.py "is temporary email safe"
验证：human_markers >= 2, word_count >= 1500, overall PASS

禁止：不要修改 .env，不要硬编码 API Key，不要改 Stage 1 和 Stage 5
