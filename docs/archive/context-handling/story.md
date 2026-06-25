Feature: Context handling — disk-first Nicki, minimal parent prompt

  As a Nicki operator
  I want the parent agent to pass only my latest message and Nicki to bootstrap from disk every response
  So that pipeline steps do not accumulate parent chat noise or stale transcript context

  Background:
    Given Nicki subagents already run in isolated context
    And context pollution comes from the parent summarizing chat into the Task prompt and from resume accumulating prior Nicki transcript

  Scenario: Parent invokes Nicki with minimal prompt only
    Given the user addresses Nicki by name or continues an in-progress Nicki session
    When the parent agent invokes Task with subagent_type nicki
    Then the Task prompt contains only the user's latest message (nicki prefix may be stripped)
    And the parent does not summarize prior chat, pipeline state, investigation, or file contents into the prompt
    And the parent does not re-read global-status.json or status.json on behalf of Nicki

  Scenario: Fresh Task each Nicki step — no resume
    Given Nicki was invoked earlier in the same parent chat
    When the user sends another Nicki-directed message
    Then the parent invokes a fresh Task with subagent_type nicki
    And the parent does not use resume with a prior Nicki subagent id
    And nicki-default.mdc Stay on Nicki guidance reflects fresh Task per step

  Scenario: Nicki bootstraps from disk before every response
    Given Nicki is activated for a pipeline step
    When Nicki routes or spawns a sheep
    Then Nicki reads global-status.json then status.json at status_path then routing.yaml before acting
    And Nicki derives current step position only from disk — not from chat or parent prompt summary
    And Nicki reads validation YAML only when artifacts.review_validation is set
    And Nicki reads the spec artifact only for the open_questions gate before subtasks

  Scenario: Hooks and injection are out of scope for this task
    Given P1-16 context-handling scope is minimal prose changes to two files
    When implementation is planned
    Then sessionStart hooks, subagentStart inject, and preToolUse Task inject are not required
    And README or NICKI.md updates are not required unless a later spec explicitly includes them
