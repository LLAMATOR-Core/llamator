# Attacks

This section provides an overview of all available attacks.

## Single-stage attacks

### OWASP [LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) Prompt Injection

<details>
<summary><strong>Adversarial Suffix</strong></summary>

In code name: `suffix`

Uses a specially crafted suffix to bypass LLM filters and restrictions, forcing the model to generate prohibited or harmful content despite the original query. Evaluates the model's vulnerability to input data manipulation.

_Original Paper: <https://arxiv.org/abs/2307.15043>, Original Code: <https://github.com/llm-attacks/llm-attacks>_

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/suffix.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Aim Jailbreak</strong></summary>

In code name: `aim_jailbreak`

Probes an LLM's ethical compliance by eliciting detailed instructions on illegal activities, using the Nicolo Machiavelli character roleplay.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/aim.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Base64 Injection</strong></summary>

In code name: `base64_injection`

Challenges the LLM with a dataset of lines, encoded into base64.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/base64_injection.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Best-of-N Jailbreak</strong></summary>

In code name: `bon`

Probes the LLM resilience against Best-Of-N attack.

_Original Paper: <https://arxiv.org/abs/2412.03556>, Original Code: <https://github.com/jplhughes/bon-jailbreaking>_

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/bon.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Complimentary Transition</strong></summary>

In code name: `complimentary_transition`

Evaluates the LLM's ability to maintain content moderation standards when transitioning from a compliment to a new task. It assesses the LLM's ability to maintain defined boundaries when prompted to switch topics.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/complimentary_transition.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Do Anything Now Jailbreak</strong></summary>

In code name: `do_anything_now_jailbreak`

Probes an LLM's resilience against performing explicitly forbidden activities using the "Do Anything Now" (DAN) character roleplay technique.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/dan.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Do Anything Now Jailbreak (RU)</strong></summary>

In code name: `RU_do_anything_now_jailbreak`

Probes a Russian-language LLM's resilience against performing explicitly forbidden activities using the "Do Anything Now" (DAN) character roleplay technique.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/ru_dan.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Ethical Compliance</strong></summary>

In code name: `ethical_compliance`

Evaluates the LLM's ability to resist discussions about harmful or inappropriate misconceptions on sensitive topics. This test aims to verify the model's adherence to ethical guidelines against propagating stereotypes and toxic content.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/ethical_compliance.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Harmful Behavior</strong></summary>

In code name: `harmful_behavior`

Challenges the LLM with a dataset of harmful behavior prompts.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/harmful_behavior.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Linguistic Evasion</strong></summary>

In code name: `linguistic_evasion`

Leverages the use of a non-Russian language to circumvent the restrictions or focus set by the system prompt.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/linguistic.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Past Tense Attack</strong></summary>

In code name: `past_tense`

Challenges the LLM with a dataset of harmful behavior prompts in past tense form.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/past_tense.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Shuffle Inconsistency</strong></summary>

In code name: `shuffle`

Attempts to bypass LLM's defense mechanism by randomly shuffling elements in input harmful prompt.

_Original Paper: <https://arxiv.org/html/2501.04931>_

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/shuffle.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Typoglycemia Attack</strong></summary>

In code name: `typoglycemia_attack`

Attempts to exploit a text processing vulnerability in LLMs that can cause incorrect responses by removing random characters from words.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/typoglycemia.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Typoglycemia Attack (RU)</strong></summary>

In code name: `RU_typoglycemia_attack`

Attempts to exploit a text processing vulnerability in Russian-language LLMs that can cause incorrect responses by removing random characters from words.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/ru_typoglycemia.py">View code on GitHub</a>
</details>

<details>
<summary><strong>UCAR</strong></summary>

In code name: `ucar`

Probes an LLM's adherence to content restrictions when explicitly requested to ignore such filters. It assesses the robustness of the LLM's content moderation systems against direct challenges.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/ucar.py">View code on GitHub</a>
</details>

<details>
<summary><strong>UCAR (RU)</strong></summary>

In code name: `RU_ucar`

Probes a Russian-language LLM's adherence to content restrictions when explicitly requested to ignore such filters. It assesses the robustness of the LLM's content moderation systems against direct challenges.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/ru_ucar.py">View code on GitHub</a>
</details>

## Multi-stage attacks

<details>
<summary><strong>What Drives the Multi-stage?</strong></summary>

Multi-stage attacks are inspired by the [Jailbreaking Black Box Large Language Models in Twenty Queries (PAIR)](https://arxiv.org/html/2310.08419) paper.

For managing a multi-stage interaction between an attacker and tested chat clients, the `MultiStageInteractionSession` class is available [[source]](https://github.com/RomiconEZ/llamator/blob/release/src/llamator/client/chat_client.py). It contains the following properties:
 * `attacker_session` is the session for the attacker.
 * `tested_client_session` is the session for the tested client.
 * `stop_criterion` is an optional function that determines whether to stop the conversation based on the tested client's responses.
 * `history_limit` is the maximum allowed history length for the attacker.
 * `tested_client_response_handler` is an optional function that handles the tested client's response before passing it to the attacker.
 * `current_step` is the current step of the attacker.
 * `refine_args` are additional positional arguments for the `tested_client_response_handler`.
 * `refine_kwargs` are additional keyword arguments for the `tested_client_response_handler`.

The `multistage_depth` parameter for using in `history_limit` can be extracted from the attack's kwargs as follows:
```python
 self.multistage_depth = kwargs.get("multistage_depth", 20)
```
</details>

### OWASP [LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) Continuous Prompt Injection

<details>
<summary><strong>Crescendo</strong></summary>

In code name: `crescendo`

Challenges the LLM with a dataset of harmful behavior prompts using Crescendo strategy, operates by engaging the LLM in a series of escalating conversational turns, and multistage refinement.

_Original Paper: <https://arxiv.org/abs/2404.01833>_

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/crescendo.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Harmful Behavior Multistage</strong></summary>

In code name: `harmful_behavior_multistage`

Challenges the LLM with a dataset of harmful behavior prompts using multistage refinement.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/harmful_behavior_multistage.py">View code on GitHub</a>
</details>

### OWASP [LLM07:2025](https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/) System Prompt Leakage

<details>
<summary><strong>System Prompt Leakage</strong></summary>

In code name: `system_prompt_leakage`

Challenges the LLM with datasets of malicious prompts to extract system instructions using multistage refinement.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/system_prompt_leakage.py">View code on GitHub</a>
</details>

### OWASP [LLM09:2025](https://genai.owasp.org/llmrisk/llm092025-misinformation/) Misinformation

<details>
<summary><strong>Logical Inconsistencies Test</strong></summary>

In code name: `logical_inconsistencies`

Attacks the LLM system during a multistage conversation to generate logical inconsistencies in answers using antonyms, negations, and paraphrases based on the system's domain.

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/logical_inconsistencies.py">View code on GitHub</a>
</details>

<details>
<summary><strong>Sycophancy Test</strong></summary>

In code name: `sycophancy`

Attacks the LLM system during a multistage conversation using the argumentum ad verecundiam method based on the system's domain.

_Original Paper: <https://arxiv.org/abs/2310.13548>_

<a href="https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/sycophancy.py">View code on GitHub</a>
</details>