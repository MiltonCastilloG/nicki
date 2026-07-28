Feature: Clinical profile per patient

  As a therapist
  I want to produce and update a clinical profile per patient based on that patient's session history
  So that I have a synthesized, up-to-date clinical summary without re-reading every session's analysis myself

  Background:
    Given a patient exists on the PatientDetail page
    And a "Generate/Update Clinical Profile" control is shown there, after the "Sessions" header and above the upload card
    And synthesis uses only each session's stored analysis (results_json) — never raw transcripts

  Scenario: Generating a profile from completed sessions
    Given the patient has at least one session with status "complete"
    When the therapist presses the clinical profile control
    Then a narrative clinical profile is synthesized from the analyses of all completed sessions for that patient
    And the profile is persisted on the patient record along with the time it was generated
    And the profile and its timestamp are displayed on the page immediately

  Scenario: No completed sessions to synthesize
    Given the patient has zero sessions with status "complete"
    When the therapist presses the clinical profile control
    Then no profile is generated
    And an inline error is shown stating there are no completed sessions to analyze

  Scenario: Viewing a previously generated profile
    Given the patient already has a persisted clinical profile from an earlier generation
    When the therapist opens the PatientDetail page for that patient
    Then the existing profile text and its last-updated timestamp are shown without the therapist needing to press the control again

  Scenario: Regenerating replaces the previous profile
    Given the patient already has a persisted clinical profile
    And additional sessions have completed since it was generated
    When the therapist presses the clinical profile control again
    Then the profile is fully regenerated from all currently completed sessions
    And the previous profile text and timestamp are replaced by the new ones, with no merge with the prior profile

  Scenario: Generation fails
    Given the therapist presses the clinical profile control
    When the synthesis call fails due to an LLM or network error
    Then a generic error message is shown
    And any previously persisted profile is left unchanged
