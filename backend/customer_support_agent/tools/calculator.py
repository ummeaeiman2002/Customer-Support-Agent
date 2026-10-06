from __future__ import annotations

import ast
import operator

ALLOWED_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

ALLOWED_UNARY = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class CalculatorError(Exception):
    """Raised when a calculator expression is invalid."""


def validate(expression: str) -> str:
    if not isinstance(expression, str) or not expression.strip():
        raise CalculatorError("Expression must be a non-empty string.")
    expression = expression.strip()
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError(f"Not a valid expression: {expression!r}") from exc
    _assert_allowed(tree.body)
    return expression


def evaluate(expression: str) -> str:
    validate(expression)
    tree = ast.parse(expression.strip(), mode="eval")
    return _format(_evaluate(tree.body))


def _assert_allowed(node: ast.AST) -> None:
    if isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise CalculatorError("Only numbers are allowed.")
        return
    if isinstance(node, ast.BinOp):
        if type(node.op) not in ALLOWED_BINARY:
            raise CalculatorError(f"Operator not allowed: {type(node.op).__name__}")
        _assert_allowed(node.left)
        _assert_allowed(node.right)
        return
    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in ALLOWED_UNARY:
            raise CalculatorError(f"Operator not allowed: {type(node.op).__name__}")
        _assert_allowed(node.operand)
        return
    raise CalculatorError(
        f"Only numbers and + - * / // % ** ( ) are allowed, got: "
        f"{type(node).__name__}"
    )


def _evaluate(node: ast.AST) -> float | int:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        func = ALLOWED_BINARY[type(node.op)]
        try:
            result = func(left, right)
        except ZeroDivisionError as exc:
            raise CalculatorError("Division by zero.") from exc
        except OverflowError as exc:
            raise CalculatorError("Result is too large.") from exc
        return result
    if isinstance(node, ast.UnaryOp):
        return ALLOWED_UNARY[type(node.op)](_evaluate(node.operand))
    raise CalculatorError("Unsupported expression.")


def _format(result: float | int) -> str:
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    if isinstance(result, float):
        return f"{result:.10g}"
    return str(result)


CALCULATOR_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Evaluate an arithmetic expression and return the exact result.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression, e.g. '49 * 3'.",
                }
            },
            "required": ["expression"],
        },
    },
}
