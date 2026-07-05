# Phase 9 Context: Manager Agent

## Purpose
Implement the `ManagerAgent` to orchestrate multi-agent execution flow and coordinate session memory.

## Requirements
- **AGENT-05**: Implement ManagerAgent orchestrating execution flow and coordinating session memory.

## Context
This agent is the central orchestrator that chains all specialized agents (Query -> Utilization -> Forecast -> Recommendation) in sequence. It manages a shared state context and maintains session memory to enable contextual follow-up inquiries.
