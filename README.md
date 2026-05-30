# Projet 10 OpenClassrooms - Bottleneck

## Objectif

Automatiser le pipeline de transformation de données de BottleNeck avec Kestra.

## Technologies utilisées

- Kestra
- Python
- DuckDB
- Docker
- SQL

## Structure du projet

- kestra/ : workflow YAML
- scripts/ : scripts Python
- sql/ : scripts DuckDB
- tests/ : contrôles qualité

## Contrôles qualité

- absence de doublons
- absence de valeurs manquantes
- cohérence des volumes
- cohérence du chiffre d'affaires
- détection des vins premium via z-score

## Exécution

```bash
docker compose up --build