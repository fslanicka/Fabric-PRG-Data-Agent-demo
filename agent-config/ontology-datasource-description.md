# Ontology Data Source Description (Fabric IQ)

> **Copy the content below (between the --- markers) into the "Description" field for your Ontology data source in the Fabric Data Agent configuration.**

---

This ontology provides a unified semantic model of Prague Airport operations, defining 7 business entity types (Flight, Airline, Airport, WeatherObservation, GateAssignment, CrewMember, MaintenanceEvent) and their relationships. It connects data from both the Lakehouse (flight analytics) and Eventhouse (operational data) into a single navigable graph. Use this data source for questions about relationships between entities, multi-hop traversals (e.g., "which crew flew delayed flights during storms"), cross-domain reasoning, impact analysis, and any query that requires connecting information across the Lakehouse and Eventhouse data sources.

---
