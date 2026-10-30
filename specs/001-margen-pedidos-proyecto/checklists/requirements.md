# Specification Quality Checklist: Margen de pedidos por proyecto

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-30
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- Validación del 2026-10-30, iteración 2. En la primera pasada faltaban escenarios para la sesión de 30 días, el precio de cabecera frente a las líneas, la clasificación de horas, el periodo por fecha o ejercicio, la moneda y el plan de cuentas. El relato inicial mezclaba coste directo y coste contable. Esos puntos quedaron corregidos en `spec.md`.
- No quedan marcadores [NEEDS CLARIFICATION]. Los tres puntos de más impacto (fórmula de margen bruto y neto, clasificación de horas y proyecto repetido) están cerrados con supuestos en la sección Assumptions, listos para revisarse en `/speckit-clarify`.
- `/speckit-clarify` pregunta como máximo 5 veces por ejecución, de una en una. No cubre una tanda de 50 preguntas.
