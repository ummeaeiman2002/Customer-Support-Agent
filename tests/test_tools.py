import pytest

from customer_support_agent.tools.calculator import (
    CalculatorError,
    evaluate,
    validate,
)


def test_multiplication():
    assert evaluate("49 * 3") == "147"


def test_addition_and_precedence():
    assert evaluate("2 + 3 * 4") == "14"


def test_division_result_formatting():
    assert evaluate("10 / 4") == "2.5"
    assert evaluate("10 / 5") == "2"


def test_parentheses_and_power():
    assert evaluate("(2 + 3) ** 2") == "25"


def test_negative_numbers():
    assert evaluate("-7 + 3") == "-4"


def test_float_result():
    assert evaluate("1 / 3") == "0.3333333333"


def test_division_by_zero():
    with pytest.raises(CalculatorError, match="Division by zero"):
        evaluate("1 / 0")


def test_rejects_letters():
    with pytest.raises(CalculatorError):
        evaluate("abc")


def test_rejects_empty_expression():
    with pytest.raises(CalculatorError):
        evaluate("   ")


def test_rejects_function_calls():
    with pytest.raises(CalculatorError):
        evaluate("__import__('os')")


def test_rejects_strings():
    with pytest.raises(CalculatorError):
        evaluate("'a' + 'b'")


def test_validate_returns_normalized_string():
    assert validate("  1 + 1  ") == "1 + 1"
