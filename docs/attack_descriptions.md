# Attacks

This section provides an overview of all available attacks.

## Single-stage attacks

### OWASP [LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) Prompt Injection

<details>
<summary><strong>Adversarial Suffix</strong></summary>

In code name: `suffix`

Uses a specially crafted suffix to bypass LLM filters and restrictions, forcing the model to generate prohibited or harmful content despite the original query. Evaluates the model's vulnerability to input data manipulation.

_Original Paper: <https://arxiv.org/abs/2307.15043>, Code: <https://github.com/llm-attacks/llm-attacks>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/suffix.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Aim Jailbreak</strong></summary>

In code name: `aim_jailbreak`

Probes an LLM's ethical compliance by eliciting detailed instructions on illegal activities, using the Nicolo Machiavelli character roleplay.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/aim.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Base64 Injection</strong></summary>

In code name: `base64_injection`

Challenges the LLM with a dataset of lines, encoded into base64.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/base64_injection.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Best-of-N (BoN) Jailbreak</strong></summary>

In code name: `bon`

Probes the LLM resilience against Best-Of-N (BoN) attack by randomly transform symbols in input harmful prompt.

_Original Paper: <https://arxiv.org/abs/2412.03556>, Code: <https://github.com/jplhughes/bon-jailbreaking>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/bon.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Deceptive Delight</strong></summary>

In code name: `deceptive_delight`

Tests LLM's vulnerability to distraction and context manipulation by embedding unsafe content alongside benign topics in three messages.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/deceptive_delight.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Dialogue Injection: Continuation</strong></summary>

In code name: `dialogue_injection_continuation`

Probes an LLM's ethical compliance by eliciting detailed instructions on illegal activities, using the conversation simulation technique by using few-shot system prompting and unfinished assitant response at the end. Built according to the paper.

_Original Paper: <https://arxiv.org/abs/2503.08195>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/dialogue_injection_continuation.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Dialogue Injection: Developer mode</strong></summary>

In code name: `dialogue_injection_devmode`

Probes an LLM's ethical compliance by eliciting detailed instructions on illegal activities, using the conversation simulation technique to mislead the LLM with "Developer mode activation".

_Original Paper: <https://arxiv.org/abs/2503.08195>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/dialogue_injection_devmode.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Do Anything Now (DAN) Jailbreak</strong></summary>

In code name: `dan`

Probes an LLM's resilience against performing explicitly forbidden activities using the "Do Anything Now" (DAN) character roleplay technique.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/dan.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Ethical Compliance</strong></summary>

In code name: `ethical_compliance`

Evaluates the LLM's ability to resist discussions about harmful or inappropriate misconceptions on sensitive topics. This test aims to verify the model's adherence to ethical guidelines against propagating stereotypes and toxic content.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/ethical_compliance.py">View code on GitHub</a>
</details>

<details>
<summary><strong>HarmBench</strong></summary>

In code name: `harmbench`

Challenges the LLM with harmful behavior prompts from HarmBench (contains original and translated to Russian prompts).

_Original Paper: <https://arxiv.org/abs/2402.04249>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/harmbench.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Linguistic Evasion</strong></summary>

In code name: `linguistic_evasion`

Leverages the use of a non-Russian language to circumvent the restrictions or focus set by the system prompt.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/linguistic.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Linguistic Sandwich</strong></summary>

In code name: `linguistic_sandwich`

Exploits attention blink phenomena by hiding adversarial questions between innocent questions in low-resource languages. The attack leverages the concept that LLMs may have reduced attention when processing mixed low-resource languages.

_Original Paper: <https://arxiv.org/abs/2404.07242v1>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/linguistic_sandwich.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Shuffle Inconsistency</strong></summary>

In code name: `shuffle`

Attempts to bypass LLM's defense mechanism by randomly shuffling elements in input harmful prompt.

_Original Paper: <https://arxiv.org/abs/2501.04931>_

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/shuffle.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Time Machine</strong></summary>

In code name: `time_machine`

Uses an attack model to dynamically transform prompts into historical or future contexts to test temporal framing vulnerabilities.

_Original Paper: <https://arxiv.org/abs/2407.11969v2>, Code: <https://github.com/tml-epfl/llm-past-tense>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/time_machine.py">View code on GitHub</a>
</details>

<details>
<summary><strong>UCAR Jailbreak</strong></summary>

In code name: `ucar`

Probes an LLM's adherence to content restrictions when explicitly requested to ignore such filters. It assesses the robustness of the LLM's content moderation systems against direct challenges.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/ucar.py">View code on GitHub</a>
</details>

## Multi-stage attacks

<details>
<summary><strong>What Drives the Multi-stage?</strong></summary>

Multi-stage attacks are inspired by the [Jailbreaking Black Box Large Language Models in Twenty Queries (PAIR)](https://arxiv.org/abs/2310.08419) paper.

For managing a multi-stage interaction between an attacker and tested chat clients, the `MultiStageInteractionSession` class is available [[source]](https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/client/chat_client.py). It contains the following properties:
 * `attacker_session` is the session for the attacker.
 * `tested_client_session` is the session for the tested client.
 * `stop_criterion` is an optional function that determines whether to stop the conversation based on the tested client's responses.
 * `history_limit` is the maximum allowed history length for the attacker.
 * `tested_client_response_handler` is an optional function that handles the tested client's response before passing it to the attacker.
 * `current_step` is the current step of the attacker.
 * `refine_args` are additional positional arguments for the `tested_client_response_handler`.
 * `refine_kwargs` are additional keyword arguments for the `tested_client_response_handler`.
</details>

### OWASP [LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) Continuous Prompt Injection

<details>
<summary><strong>AutoDAN-Turbo</strong></summary>

In code name: `autodan_turbo`

Implements the AutoDAN-Turbo attack methodology which uses a lifelong agent for strategy self-exploration to jailbreak LLMs. This attack automatically discovers jailbreak strategies without human intervention and combines them for more effective attacks.

_Original Paper: <https://arxiv.org/abs/2410.05295v3>, Code: <https://github.com/SaFoLab-WISC/AutoDAN-Turbo>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/autodan_turbo.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Crescendo</strong></summary>

In code name: `crescendo`

Challenges the LLM with a dataset of harmful behavior prompts using Crescendo strategy, operates by engaging the LLM in a series of escalating conversational turns, and multistage refinement.

_Original Paper: <https://arxiv.org/abs/2404.01833>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/crescendo.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Prompt Automatic Iterative Refinement (PAIR)</strong></summary>

In code name: `pair`

Challenges the LLM with a dataset of adversarial prompts using multistage refinement with judge model scoring.
    Original Paper: https://arxiv.org/abs/2310.08419v4, Code: https://github.com/patrickrchao/JailbreakingLLMs

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/pair.py">View code on GitHub</a>
</details>

### OWASP [LLM07:2025](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/) System Prompt Leakage

<details>
<summary><strong>System Prompt Leakage</strong></summary>

In code name: `system_prompt_leakage`

Challenges the LLM with datasets of malicious prompts to extract system instructions using multistage refinement.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/system_prompt_leakage.py">View code on GitHub</a>
</details>

### OWASP [LLM09:2025](https://genai.owasp.org/llmrisk/llm092025-misinformation/) Misinformation

<details>
<summary><strong>Logical Inconsistencies Test</strong></summary>

In code name: `logical_inconsistencies`

Attacks the LLM system during a multistage conversation to generate logical inconsistencies in answers using antonyms, negations, and paraphrases based on the system's domain.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/logical_inconsistencies.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Sycophancy Test</strong></summary>

In code name: `sycophancy`

Attacks the LLM system during a multistage conversation using the argumentum ad verecundiam method based on the system's domain.

_Original Paper: <https://arxiv.org/abs/2310.13548>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/sycophancy.py">View code on GitHub</a>

</details>

## VLM attacks

See an example with <a href="https://github.com/LLAMATOR-Core/llamator/blob/release/examples/llamator-vlm-attacks.ipynb">VLM attacks</a>.

### OWASP [LLM09:2025](https://genai.owasp.org/llmrisk/llm092025-misinformation/) Misinformation

<details>
<summary><strong>Lowres Documents Hallucination Attack</strong></summary>

In code name: `vlm_lowres_docs`

Test class for VLM responses for low resolution documents.
The idea is that we provide model with unreadable document and ask to describe its contents.
The goal is to see whether model will signal that the document is unreadable or hallucinate about the contents.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/vlm_lowres_docs.py">View code on GitHub</a>
</details>

<details>
<summary><strong>M-Attack</strong></summary>

In code name: `vlm_m_attack`

Test VLM for M-Attack, which adds noise to the image to make VLM see it as a different image.

_Original Paper: <https://arxiv.org/abs/2503.10635>_

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/vlm_m_attack.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Text Hallucination Attack</strong></summary>

In code name: `vlm_text_hallucination`

Test class for VLM text hallucination attacks.
The idea is to give model and image which contains only text and ask it to describe it.
The goal is to see whether model will describe text or hallucinate with the description of an object written in text.

<a href="https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/vlm_text_hallucination.py">View code on GitHub</a>
</details>
