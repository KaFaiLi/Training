# Structured Prompts with XML Tags: Claude (Anthropic) vs GPT-4o (OpenAI)

Modern LLMs like Claude and GPT-4o benefit from **structured prompts** using explicit delimiters. Anthropic’s official guidance even calls XML tagging a “game-changer” for Claude, since it “help\[s] Claude parse your prompts more accurately, leading to higher-quality outputs”. OpenAI similarly notes that clear delimiters (Markdown headings, XML tags, etc.) improve GPT-4.1’s adherence to instructions. In practice, using XML tags (e.g. `<instructions>…</instructions>`, `<example>…</example>`) can help both models distinguish sections (context vs. instruction vs. examples) and reduce misinterpretation. Below we compare the two models across key dimensions.

## 1. Output Clarity, Coherence, and Accuracy

**Claude (Anthropic):** Anthropic’s docs emphasize that tagging **improves clarity and accuracy**. By wrapping instructions, context, or examples in distinct tags, Claude is less likely to “mix up” parts of the prompt. For instance, after adding tags like `<instructions>` and `<formatting>`, Claude produced a **tightly structured financial report** (with numbered sections and bullet points), whereas the same prompt without tags yielded a muddled output. Similarly, a legal-analysis example shows Claude producing clearly separated `<findings>` and `<recommendations>` sections when prompted with XML tags. In summary, Anthropic reports that XML prompts “reduce errors caused by Claude misinterpreting parts of \[the] prompt” and make outputs easier to parse.

**GPT-4o (OpenAI):** OpenAI’s guidance recommends Markdown as the default formatting, but explicitly states XML also performs well. The GPT-4.1 Prompting Guide notes that GPT-4.1 has “improved adherence to information in XML,” and that XML “performed well” in long-context tests. In practice, many users find GPT-4’s output quality **similar when using Markdown or XML tags**. One experiment reported that GPT-4’s answers with XML-formatted prompts were comparable to Markdown, while plain-text prompts (no delimiters) gave weaker results. A LinkedIn analysis concurs that GPT-4 understands XML “with OpenAI documentation advising the use of delimiters, including XML tags, to help models distinguish prompt sections”. In other words, GPT-4o can leverage the unambiguous structure of XML: it generally follows such tags as cues to improve focus. However, unlike Claude, GPT-4 was not specifically “trained on” XML; rather, it treats XML tags as strong hints. Community feedback suggests both models benefit from explicit structure, but Claude’s outputs may show more drastic improvement from adding tags than GPT-4’s (which may already do well with just Markdown headings and bullet lists).

**Key Points:** Adding XML tags tends to make outputs more **structured and faithful**. For Claude, official docs and user examples confirm it prevents confusion (the model “misinterpreting parts of your prompt”). For GPT-4o, structured prompts (XML or Markdown) also yield more coherent answers than unstructured text. In both cases, delimiters help separate multi-part instructions, examples, or context so the model can follow each part correctly.

## 2. Interpretability & Instruction-Following

Well-structured prompts make the model’s task explicit. **Claude** often treats XML tags as meaningfully as possible. For example, a “power user tip” in Anthropic’s docs is to combine tags with chain-of-thought cues (like `<thinking>` vs. `<answer>`), which yields “super-structured, high-performance prompts”. In practice, instructing Claude with `<thinking>` blocks lets it separate its reasoning from the final answer in output, making its process transparent. Even Anthropic’s leaked system prompts use XML heavily, so the model is accustomed to interpreting tags. A Claude prompt engineer notes: “Claude was trained with XML tags in the training data… using XML tags like `<example>`, `<document>`, etc. … can help guide Claude’s output”. In short, clear tags mean Claude follows instructions more precisely, and its outputs can be easily post-processed by parsing those tags.

**GPT-4o (OpenAI):** GPT-4.1 is also optimized for instruction-following. OpenAI recommends a structured approach (rules, bullet points, examples) for instructions. A technical guide explicitly suggests using delimiters (including XML tags) to delineate sections and prevent prompt injection. While GPT-4 may not have been explicitly “trained on” XML, it reliably treats tags as delimiters. For instance, an OpenAI guide encourages placing instructions at the start/end of context or within headers for clarity; similarly, tags like `<instructions>` serve that purpose. Models generally follow such explicit cues closely. In practice, specifying structured sections improves reliability: one user found that both XML and Markdown structure “often improve performance compared to plain text prompts”. Thus, GPT-4o will respond to an `<instructions>` block by focusing on those rules. This enhances interpretability: humans can read the prompt structure, and the model is less likely to overlook or misapply a rule.

**Summary:** Both models benefit when instructions are clearly demarcated. Claude’s docs and experts emphasize XML tags for this purpose. OpenAI’s guides likewise encourage explicit sections (via headers or tags) for reliable instruction following. In practice, a prompt that says:

```xml
<instructions>
1. Compare values A and B.
2. Output in bullet points.
</instructions>
<data>…</data>
```

will lead Claude to put each step’s answer inside bullet points, and GPT-4 to similarly format its reply. Explicit tags thus **improve interpretability** for both user and model.

## 3. Structured Output Generation (XML, JSON, Markdown)

When the *output* itself must be structured (XML/JSON/Markdown), tags in the prompt can enforce or signal format. **Claude:** Anthropic provides a “prefill” technique. For example, to get JSON output, the prompt might include `<json>` and a partial JSON start. Claude then continues in JSON until a closing tag. One Anthropic example shows prefixing:

```
Here is the JSON: 
<json>
{ 
```

so Claude “is primed to complete the JSON”. The docs even recommend using stop sequences like `</json>` to signal the end. In general, if you wrap desired output sections in tags (e.g. `<answer>…</answer>` or `<findings>…</findings>`), Claude will produce those tags in its response, making parsing trivial. The legal contract example demonstrates this: the assistant’s response included `<findings>` and `<recommendations>` sections as requested. Thus, for Claude, including specific XML tags for output (and even prefilling them) yields reliably formatted output.

**GPT-4o:** GPT-4o can also generate structured outputs by instruction. OpenAI now even offers a dedicated “JSON Mode” and function-calling API so that GPT-4o returns valid JSON. Even without those features, simply telling GPT to “reply in JSON with this format:” works very well (users report GPT-4 will “do a really good job” with JSON prompts). In prompt engineering guides, the advice is to “request structured output like HTML or JSON for easier parsing”. For example, one might include in the prompt: `Output=JSON` or start the answer section with a code block:

```json
<expectedOutput>{
  "name": ..., 
  "age": ...
}
</expectedOutput>
```

Then GPT-4 will usually produce valid JSON inside those tags. Unlike Claude, GPT-4 doesn’t have a native `<json>` tag in its system, but asking for JSON or using triple backticks often suffices. For Markdown, GPT-4 and Claude both natively output Markdown formatting (GPT-4 replies often default to Markdown). But if strict structure is needed, XML tags can serve as delimiters for any format. For example:

```xml
<answer>
- **Pros:** ...
- **Cons:** ...
</answer>
```

ensures the content is easily extracted. In practice, neither model enforces a format on its own; you must explicitly define it. (GPT-4 can now be asked to follow a JSON schema with function calling, which is a more reliable channel for code or JSON output.)

**Takeaway:** Tagging helps guarantee structured outputs. Claude’s XML-centric toolkit (prefilled tags, stop sequences) is particularly geared toward this. GPT-4o offers similar results via explicit instruction (“in JSON” or “format as YAML”) or built-in modes. In both cases, a prompt like:

```xml
<answer>
...content...
</answer>
```

or its JSON analog, yields a machine-friendly response.

## 4. Performance & Benchmarks

There are no public, head-to-head benchmarks explicitly comparing **XML-tagged prompts vs. plain prompts** on Claude or GPT-4o. However, available guidance and user reports imply performance differences. For Claude, structured prompts are said to increase consistency and accuracy. For GPT-4o, OpenAI’s own evaluations found XML worked well even in long-context tasks, whereas JSON prompts were “particularly poor”. A comparative benchmark (e.g. Helicone’s GPT-4.1 vs Claude coding tests) showed GPT-4.1 outperforming Claude 3.7 on code tasks, but these tests did not isolate prompt format effects. We did find no formal academic paper comparing XML vs non-XML prompting. Instead, evidence is mainly anecdotal:

* **Prompt clarity:** Consistently, users find XML/Markdown prompts reduce errors. For example, one practitioner noted that the only major drop in quality was when using “plain text” prompts – whereas Markdown and XML were similar.
* **Token costs:** XML’s verbosity costs more tokens (each tag adds tokens). A LinkedIn article notes XML prompts can be heavier, potentially increasing latency. GPT-4’s guide even points out XML tags inflate token count (compared to Markdown). In very large contexts, this might slow generation. But both Claude and GPT-4 handle nested XML without issues. Markdown or YAML are more compact alternatives (YAML often uses \~15% fewer tokens than JSON/XML).

In summary, **no systematic benchmark** exists for “with vs without XML tagging,” but expert consensus is that tags *help structure* at a slight token cost. The qualitative benefit (more accurate, consistent output) is usually worth the overhead. When building mission-critical or multi-part prompts, developers routinely prefer XML/Markdown over ad-hoc plain text for both models.

## 5. Developer Insights & Best Practices

**Anthropic (Claude) Guidelines:** Anthropic’s docs and blog posts strongly endorse XML. Their prompt-engineering page lists bullet points: *“Clarity: separate parts… Accuracy: reduce errors…Parseability: easier extraction”*. They recommend making tag names meaningful (e.g. `<contract>`, `<findings>`) and to consistently nest tags for hierarchy. Prompts should alternate `<user>`/`<assistant>` tags in the API. Analysts and prompt engineers emphasize using `<examples>` for few-shot prompts and `<thinking>` for chain-of-thought. In workshops, Anthropic engineers noted “Claude was trained with XML tags in the training data”. Thus developers often start a prompt with something like:

```xml
<system>This is the system prompt setting.</system>
<user>
  <instructions>Summarize the document below.</instructions>
  <document>...</document>
</user>
<assistant />
```

to clearly delineate roles. Using these tags helps Claude remain in role and follow instructions. Anthropic also provides tools like *prefill* (for JSON/XML output) and *stop sequences* for closing tags.

**OpenAI (GPT-4o) Guidance:** OpenAI’s prompt guide (and API docs) advise clear instructions, examples, and delimiters. They suggest Markdown headings (##) or XML-like tags to mark sections. A prompt framework summary explicitly says: “Use `“””` and XML tags frequently (ChatGPT and Claude are specifically trained with XML tag prompts…)”, implying community-perceived parity. Community threads confirm XML tags are “encouraged by all of Anthropic, Google, and OpenAI LLMs”. For GPT-4, tips include: place important instructions both at the start and end of context, use bullet lists for steps, and specify formatting requirements. For structured data, use either the newer function-calling API or simply instruct the model to output JSON/YAML. Many prompt toolkits (LangChain, PromptFoo) even let you write prompts in YAML or JSON for convenience. In short, for GPT-4o, best practices are: clearly segment sections (with any delimiters), use examples, and explicitly request formats.

**Example Prompts:** Below is a simplified comparative example. In each case, the *intent* is the same, but the second prompt uses XML tags to structure it:

* *Without XML:*

  ```text
  You are a tutor. Answer the question: What is the square root of 16? Be concise.
  ```
* *With XML tags:*

  ```xml
  <role>You are a math tutor.</role>
  <question>What is the square root of 16?</question>
  <instructions>Answer in one sentence, explain the reasoning.</instructions>
  ```

Claude, seeing the `<question>` and `<instructions>` tags, will clearly separate the answer into its `<answer>` tags if asked. GPT-4o, given the same XML prompt, will likewise use those tags or headers to format the reply. In both models, the tag-based version is far more explicit and unambiguous for multi-part instructions.

**Community Experiments:** Users on forums report similar findings for both models. For example, one GPT user said “I use XML tags in my prompt templates, and they work well” (they observed no loss of performance). Another noted that asking Claude to put its reasoning in a `<scratchpad>` tag made the output “more interesting,” implying better chain-of-thought capture. Community prompt libraries often include XML-based templates (e.g. `<task>`, `<input>`, `<output>` tags).

## 6. Summary of Findings

| Aspect                               | Claude (Anthropic)                                                                                                                                                                                                                                       | GPT-4o (OpenAI)                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Official Guidance**                | *“XML tags can be a game-changer… higher-quality outputs.”*Recommended to wrap instructions, data, examples in tags.                                                                                                                                     | Advised to use clear format (Markdown, triple quotes, or XML) as needed. Both Markdown and XML “perform well”.                                                                                                                                                                                                                                                  |
| **Training Background**              | Trained extensively on XML-like prompts; internal use of XML in system prompts. Engineers: “Claude was trained with XML tags in the training data.”                                                                                                      | Trained on diverse formats (Markdown, code, etc). Understands XML tags but no claim of special training on them; treats them as delimiters. OpenAI docs mention use of “XML tags, section titles, etc.” for structure.                                                                                                                                          |
| **Quality Impact**                   | Often sees big gains: reduces misinterpretation, yields neatly structured answers (lists, sections). Example: financial report became concise lists of bullet points.                                                                                    | Gains are positive but sometimes smaller: structured prompts (XML or MD) consistently beat freeform text. One user found XML vs MD made **minor differences** in the content of responses (both were good, plain text was worse).                                                                                                                               |
| **Instruction Following**            | Strong when prompts are explicit. Tags like `<instructions>` clearly isolate rules. FAQs and examples show Claude obeying nested tags and lists.                                                                                                         | Also strong, especially with step-by-step lists and explicit “you must” statements. GPT-4.1 “follows instructions more literally,” so clear, tagged sections help. Community notes GPT-4 will respect explicit tags if provided.                                                                                                                                |
| **Structured Outputs**               | Excellent support. Can be prefilled with `<json>` or `<xml>` tags; often used with stop sequences to produce valid output. Outputs can be parsed by looking for known tags.. Example: `<findings>` and `<recommendations>` sections in a legal analysis. | Good support via explicit instructions. GPT-4.1 offers JSON mode/function calls for guaranteed JSON. Without that, simply asking “output JSON” or using backticks yields structured results most of the time. Can also be told to use YAML/Markdown as needed.                                                                                                  |
| **Developer Tools & Best Practices** | Anthropic docs give XML-centric recipes (prefill, stop-seq, tag nesting). Prompt engineering blogs (Anthropic’s “Prompt Doctor”) echo that tags help guide output. Tools like LangChain allow building XML templates for Claude.                         | OpenAI docs (GPT-4 Prompt Guide) highlight clear instructions, examples, and indicate that XML is viable. Prompt frameworks often use Markdown by default (since GPT outputs Markdown nicely), but many engineers use XML-like templates in their code. The consensus: be explicit and use any structure (tags, headings, lists) that makes sense for the task. |

**Bottom Line:** Both Claude and GPT-4o respond well to structured prompts. Claude has **explicitly built-in incentives** to use XML-style tags (and performs especially robustly with them). GPT-4o handles XML just as a clear delimiter format. For developers, the rule of thumb is similar: whenever a prompt has multiple parts (context vs instructions vs examples), **use tags or headers to separate them**. Tables, bullet lists, or XML all help. Anthropic’s official stance is strongly pro-XML; OpenAI’s stance is “use clear structure” (whether via Markdown or XML).

In practice, designing a prompt like the example above – with `<instructions>`, `<question>`, etc. – will make **both** models’ outputs more reliable and easier to parse. The evidence (from docs and community) is that XML-based formatting generally **enhances output quality and consistency** for Claude, and **also benefits GPT-4**, especially compared to unstructured prompts. The token cost of extra tags is usually a minor trade-off for the clarity gained.

**References:** We drew on official docs and community reports. Anthropic’s prompt guide explicitly advocates XML tags. OpenAI’s documentation and cookbooks describe using delimiters (including XML). Several prompt engineering articles confirm these findings in context. These sources collectively show how XML-tagged prompts improve model performance and guidance for both Claude and GPT-4o.
