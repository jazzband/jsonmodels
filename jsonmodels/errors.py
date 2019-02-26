from typing import List, Tuple, Type


class ValidationError(RuntimeError):
    """
    The base validation error
    """


class FieldNotFound(RuntimeError):
    """ Error raised when a field is not found """
    def __init__(self, field_name: str):
        """
        :param field_name: The name of the field.
        """
        super(FieldNotFound, self).__init__('Field not found', field_name)
        self.field_name = field_name


class FieldNotSupported(ValueError):
    def __init__(self, field_type: Type):
        super(FieldNotSupported, self).__init__(
            "Can't specify value schema!", field_type
        )
        self.field_type = field_type


class ValidatorError(ValidationError):
    """
    Base error for all errors caused by a validator. These errors do not
    contain any information about which field generated them. Models
    should catch this error and convert it to a FieldValidationError.
    """


class FieldValidationError(ValidationError):
    """
    Enriches a validator error with the name of the field that caused it.
    """
    def __init__(self, model_name: str, field_name: str,
                 given_value: any, error: ValidatorError):
        """
        :param model_name: The name of the model.
        :param field_name: The name of the field.
        :param error: The validator error.
        """
        tpl = "Error for field '{name}': {error}"
        super(FieldValidationError, self).__init__(tpl.format(
            name=field_name, error=error
        ))
        self.model_name = model_name
        self.field_name = field_name
        self.given_value = given_value
        self.error = error


class RequiredFieldError(ValidatorError):
    """ Error raised when a required field has no value """
    def __init__(self):
        super(RequiredFieldError, self).__init__('Field is required!')


class RegexError(ValidatorError):
    """ Error raised by the Regex validator """

    def __init__(self, value: str, pattern: str):
        tpl = 'Value "{value}" did not match pattern "{pattern}".'
        super(RegexError, self).__init__(tpl.format(
            value=value, pattern=pattern
        ))
        self.value = value
        self.pattern = pattern


class BadTypeError(ValidatorError):
    """
    Error raised when the user gives a type that does not match the
    expected one
    """

    def __init__(self, value: any, types: Tuple, is_list: bool):
        """
        :param value: The given value.
        :param types: The accepted types.
        :param is_list: Whether the error occurred in the items of a list.
        """
        if is_list:
            tpl = 'All items must be instances of "{types}", and not "{type}".'
        else:
            tpl = 'Value is wrong, expected type "{types}", received {value}.'
        super(BadTypeError, self).__init__(tpl.format(
            types=', '.join([t.__name__ for t in types]),
            value=value,
            type=type(value).__name__
        ))
        self.value = value
        self.types = types
        self.is_array = is_list


class AmbiguousTypeError(ValidatorError):
    """
    Error that occurs if the user gives a dictionary to an embedded field
    that supports multiple types
    """

    def __init__(self, types: Tuple):
        """ The types that are allowed """
        tpl = 'Cannot decide which type to choose from "{types}".'
        super(AmbiguousTypeError, self).__init__(tpl.format(
            types=', '.join([t.__name__ for t in types])
        ))
        self.types = types


class MinLengthError(ValidatorError):
    """ Error raised by the Length validator when too few items are present """

    def __init__(self, value: list, minimum_length: int):
        """
        :param value: The given value.
        :param minimum_length: The minimum length expected.
        """
        tpl = "Value '{value}' length is lower than allowed minimum '{min}'."
        super(MinLengthError, self).__init__(tpl.format(
            value=value, min=minimum_length
        ))
        self.value = value
        self.minimum_length = minimum_length


class MaxLengthError(ValidatorError):
    """ Error raised by the Length validator when receiving too many items """

    def __init__(self, value: list, maximum_length: int):
        """
        :param value: The given value.
        :param maximum_length: The maximum length expected.
        """
        tpl = "Value '{value}' length is bigger than allowed maximum '{max}'."
        super(MaxLengthError, self).__init__(tpl.format(
            value=value, max=maximum_length
        ))
        self.value = value
        self.maximum_length = maximum_length


class MinValidationError(ValidatorError):
    """ Error raised by the Min validator """

    def __init__(self, value, minimum_value, exclusive: bool):
        """
        :param value: The given value.
        :param minimum_value: The minimum value allowed.
        :param exclusive: Whether the validation is inclusive or not.
        """
        tpl = "'{value}' is lower or equal than minimum ('{min}')." \
            if exclusive else "'{value}' is lower than minimum ('{min}')."
        super(MinValidationError, self).__init__(tpl.format(
            value=value, min=minimum_value
        ))
        self.value = value
        self.minimum_value = minimum_value
        self.exclusive = exclusive


class MaxValidationError(ValidatorError):
    """ Error raised by the Max validator """

    def __init__(self, value, maximum_value, exclusive: bool):
        """
        :param value: The given value.
        :param maximum_value: The maximum value allowed.
        :param exclusive: Whether the validation is inclusive or not.
        """
        tpl = "'{value}' is bigger or equal than maximum ('{max}')." \
            if exclusive else "'{value}' is bigger than maximum ('{max}')."
        super(MaxValidationError, self).__init__(tpl.format(
            value=value, max=maximum_value
        ))
        self.value = value
        self.maximum_value = maximum_value
        self.exclusive = exclusive


class EnumError(ValidatorError):
    """ Error raised by the Enum validator """

    def __init__(self, value: any, choices: List[any]):
        """
        :param value: The given value.
        :param choices: The allowed choices.
        """
        tpl = "Value '{val}' is not a valid choice."
        super(EnumError, self).__init__(tpl.format(val=value))
        self.value = value
        self.choices = choices
