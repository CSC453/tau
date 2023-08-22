---
title: CSC 453 Milestone 9
author: Todd Proebsting
---

# WARNING: THIS IS A DRAFT---DO NOT USE


# CSC 453 Milestone 10 (Register Assignment)

## Goal:

This milestone is to decorate/annotate an Tau's `Expr` AST with register assignments. This phase directly follows offset assignment.

## Specifications

The Tau language specification is a separate document.

The AST nodes are defined in `asts.py`.

Symbols and types are defined in `symbols.py`.



## Create `assign.py`

You will start with the supplied stub file called `assign.py` that will contain the code for annotating the `Expr` AST and Symbols with computed register assignments.

EVERY `Expr` AST node must have a `reg` field that is a string (e.g., `"r1"`, `"r2"`).  The registers are assigned in the following way:

1. The registers are numbered from `r1` to `rN`.  There are an infinite number of registers available.
2. The registers are assigned Left-to-Right, using as few registers as possible.

## Errors

This milestone only requires that you correctly annotate a correct Tau program.

## Difficulty

This milestone does not require a lot of code beyond the tree walker, which is provided.  That said, it can be a little tricky to check and infer types for some nodes.

Start early and ask questions.

## Standard Requirements

Your program must meet all the requirements outlined in the common requirements document.

