# Task archive — 02

## Task

Slug `02`. Task-spawn orchestration without leaf commands. Branch `main`.

## Story

Task subagent_type spawn only · leaf slash commands removed · thin agent shells · skills canonical · nicki-default rule entry · ad-hoc skill attachment · agent + skill docs aligned

## Outcome

Shipped. Archived at `docs/archive/02/`. All 20 subtasks checked.

## Process

**Spec** defined commandless orchestration on slice 00–01 baseline.

**Subtasks** rewrote Nicki doc, stripped slash refs from agents and skills, updated README quick start and PLAN layout.

**Execute** verified commands directory has no leaf pipeline commands and each step reachable as agent + skill pair.

**Close** archived to `docs/archive/02/`; construction source torn down.

## Decisions

Parent agent must not improvise full pipeline — suggest Nicki instead. Skills remain for ad-hoc work outside Nicki.

## Suggestions

When renaming agents in slice 03, centralize spawn map in routing.yaml to avoid doc drift.
