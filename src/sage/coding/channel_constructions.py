r"""
Channels

Given an input space and an output space, a channel takes element from
the input space (the message) and transforms it into an element of the output space
(the transmitted message).

This file contains the following elements:

    - *AbstractChannel*, the abstract class for Channels
    - *StaticErrorRateChannel*, which creates a specific number of errors in each
      transmitted message
    - *ErrorErasureChannel*, which creates a specific number of errors and a
      specific number of erasures in each transmitted message
"""

#*****************************************************************************
#       Copyright (C) 2015 David Lucas <david.lucas@inria.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.rings.finite_rings.constructor import GF
from sage.misc.prandom import randint, random
from sage.modules.free_module_element import vector
from sage.misc.abstract_method import abstract_method
from sage.combinat.cartesian_product import CartesianProduct
from sage.modules.free_module import VectorSpace

def _random_error_position(n , number_errors):
    r"""
    Returns a list of exactly ``number_errors`` random numbers between 0 and ``n-1``
    This is a helper function, for internal use only.
    This function was taken from codinglib (https://bitbucket.org/jsrn/codinglib/)
    and was written by Johan Nielsen.

    INPUT:

    - ``number_errors`` -- the number of elements in the list

    - ``n`` -- upper bound for the elements of the list

    OUTPUT:

    - A list of integers

    EXAMPLES::

        sage: sage.coding.channel_constructions._random_error_position(6, 2) # random
        [1, 4]
    """
    error_position = []
    i = 0
    while i < n and number_errors > 0:
        if random() < number_errors/(n-i):
            error_position.append(i)
            number_errors -= 1
        i += 1
    return error_position

def _random_error_vector(n, F, error_positions):
    r"""
    Return a vector of length ``n`` over ``F`` filled with random non-zero coefficients
    at the positions given by ``error_positions``.
    This is a helper function, for internal use only.
    This function was taken from codinglib (https://bitbucket.org/jsrn/codinglib/)
    and was written by Johan Nielsen.

    INPUT:

    - ``n`` -- the length of the vector

    - ``F`` -- the field over which the vector is defined

    - ``error_positions`` -- the non-zero positions of the vector

    OUTPUT:

    - a vector of ``F``

    EXAMPLES::

        sage: sage.coding.channel_constructions._random_error_vector(5, GF(2), [1,3])
        (0, 1, 0, 1, 0)
    """
    vect = [F.zero()]*n
    for i in error_positions:
        while vect[i].is_zero():
            vect[i] = F.random_element()
    return vector(F, vect)

def _tuple_to_integer(value):
    r"""
    Returns an integer from ``value``. If ``value`` is a tuple, it will return a random
    integer between its bounds.
    This is a helper function, for internal use only.

    INPUT:

    - ``value`` -- an integer or a couple of integers

    OUTPUT:

    - an integer

    EXAMPLES::

        sage: sage.coding.channel_constructions._tuple_to_integer(4)
        4

        sage: sage.coding.channel_constructions._tuple_to_integer((1,5)) # random
        3
    """
    value = value if not hasattr(value, "__iter__") else randint(value[0], value[1])
    return value





class AbstractChannel(object):
    r"""
    Abstract top-class for Channel objects.

    All channel objects must heritate from this class. To implement a channel subclass, one should
    do the following:

    - heritate from this class,

    - call the super constructor,

    - override :meth:`transmit_unsafe`.

    While not being mandatory, it might be useful to reimplement representation methods (``__repr__`` and
    ``_latex_``), along with a comparison method (``__eq__``).

    This abstract class provides the following parameters:

        - ``input_space`` -- the space of the words to transmit

        - ``output_space`` -- the space of the transmitted words
    """

    def __init__(self, input_space, output_space):
        r"""
        Initializes parameters for a Channel object.

        This is a private method, which should be called by the constructor
        of every encoder, as it automatically initializes the mandatory
        parameters of a Channel object.

        INPUT:

        - ``input_space`` -- the space of the words to transmit

        - ``output_space`` -- the space of the transmitted words

        EXAMPLES:

        We first create a new Channel subclass::

            sage: class ChannelExample(sage.coding.channel_constructions.AbstractChannel):
            ....:   def __init__(self, input_space, output_space):
            ....:       super(ChannelExample, self).__init__(input_space, output_space)

        We now create a member of our newly made class::

            sage: input = VectorSpace(GF(7), 6)
            sage: output = VectorSpace(GF(7), 5)
            sage: Chan = ChannelExample(input, output)

        We can check its parameters::

            sage: Chan.input_space()
            Vector space of dimension 6 over Finite Field of size 7
            sage: Chan.output_space()
            Vector space of dimension 5 over Finite Field of size 7
        """
        self._input_space = input_space
        self._output_space = output_space

    def transmit(self, message):
        r"""
        Returns ``message``, modified accordingly with the algorithm of the channel it was
        transmitted through.
        Checks if ``message`` belongs to the input space, and returns an exception if not.

        INPUT:

        - ``message`` -- a vector

        OUTPUT:

        - a vector of the output space of ``self``

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err = 2
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: msg = F((4, 8, 15, 16, 23, 42))
            sage: Chan.transmit(msg) # random
            (4, 14, 15, 16, 17, 42)

        If we transmit a vector which is not in the input space of ``self``::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err = 2
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: msg = (4, 8, 15, 16, 23, 42)
            sage: Chan.transmit(msg)
            Traceback (most recent call last):
            ...
            TypeError: Message must be an element of the input space for the given channel
        """
        if message in self.input_space():
            return self.transmit_unsafe(message)
        else :
            raise TypeError("Message must be an element of the input space for the given channel")

    def input_space(self):
        r"""
        Returns the input space of ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err = 2
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: Chan.input_space()
            Vector space of dimension 6 over Finite Field of size 59

        """
        return self._input_space

    def output_space(self):
        r"""
        Returns the output space of ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err = 2
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: Chan.output_space()
            Vector space of dimension 6 over Finite Field of size 59
        """
        return self._output_space
    
    @abstract_method
    def transmit_unsafe(self, message):
        r"""
        Returns ``message``, modified accordingly with the algorithm of the channel it was
        transmitted through.
        This method does not check if ``message`` belongs to the input space of``self``.

        This is an abstract method which should be reimplemented in all the subclasses of
        Channel.
        """
        raise NotImplementedError










class StaticErrorRateChannel(AbstractChannel):
    r"""
    Constructs a channel which adds a static number of errors to each message
    it transmits. The input space and the output space of this channel
    are the same.

    INPUT:

    - ``space`` -- the space of both input and output

    - ``number_errors`` -- the number of errors added to each transmitted message
      It can be either an integer of a tuple. If a tuple is passed as
      argument, the number of errors will be a random integer between the
      two bounds of the tuple.

    EXAMPLES:

    We construct a StaticErrorRateChannel which adds 2 errors
    to any transmitted message::

        sage: F = VectorSpace(GF(59), 40)
        sage: n_err = 2
        sage: Chan = channels.StaticErrorRateChannel(F, n_err)
        sage: Chan
        Static error rate channel creating 2 error(s)

    We can also pass a tuple for the number of errors::

        sage: F = VectorSpace(GF(59), 40)
        sage: n_err = (1, 10)
        sage: Chan = channels.StaticErrorRateChannel(F, n_err)
        sage: Chan
        Static error rate channel creating between 1 and 10 errors
    """

    def __init__(self, space, number_errors):
        r"""
        TESTS:
        
        If the number of errors exceeds the dimension of the input space,
        it will return an error::

            sage: F = VectorSpace(GF(59), 40)
            sage: n_err = 42
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            Traceback (most recent call last):
            ...
            ValueError: There might be more errors than the dimension of the input space
        """
        super(StaticErrorRateChannel, self).__init__(space, space)
        no_err = number_errors if not hasattr(number_errors, "__iter__") else number_errors[1]
        if no_err > space.dimension():
            raise ValueError("There might be more errors than the dimension of the input space")
        self._number_errors = number_errors

    def __repr__(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 50)
            sage: n_err = 42
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: Chan
            Static error rate channel creating 42 error(s)
        """
        if not hasattr(self.number_errors(), "__iter__"):
            return "Static error rate channel creating %s error(s)"\
                    % self.number_errors()
        else:
            no_err = self.number_errors()
            return "Static error rate channel creating between %s and %s errors"\
                    % (no_err[0], no_err[1])

    def _latex_(self):
        r"""
        Returns a latex representation of ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 50)
            sage: n_err = 42
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: Chan._latex_()
            '\\textnormal{Static error rate channel, creating }42 \\textnormal{ error(s)}'
        """
        if not hasattr(self.number_errors(), "__iter__"): 
            return "\\textnormal{Static error rate channel, creating }%s \\textnormal{ error(s)}"\
                    % self.number_errors()
        else:
            no_err = self.number_errors()
            return "\\textnormal{Static error rate channel, creating between %s and %s errors}"\
                    % (no_err[0], no_err[1])

    def __eq__(self, other):
        r"""
        Checks if ``self`` is equal to ``other``.

        EXAMPLES::
        
            sage: F = VectorSpace(GF(59), 50)
            sage: n_err = 42
            sage: Chan1 = channels.StaticErrorRateChannel(F, n_err)
            sage: Chan2 = channels.StaticErrorRateChannel(F, n_err)
            sage: Chan1 == Chan2
            True
        """
        return isinstance(other, StaticErrorRateChannel)\
                and self.input_space() == other.input_space()\
                and self.number_errors() == other.number_errors()

    def transmit_unsafe(self, message):
        r"""
        Returns ``message`` with as many errors as ``self._number_errors`` in it.
        If ``self._number_errors`` was passed as a tuple for the number of errors, it will
        pick a random integer between the bounds of the tuple and use it as the number of errors.
        This method does not check if ``message`` belongs to the input space of``self``.

        INPUT:

        - ``message`` -- a vector

        OUTPUT:

        - a vector of the output space

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err = 2
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: msg = F((4, 8, 15, 16, 23, 42))
            sage: Chan.transmit_unsafe(msg) # random
            (4, 14, 15, 16, 17, 42)
        """
        number_errors = _tuple_to_integer(self.number_errors())
        V = self.input_space()
        n = V.dimension()
        error_vector = _random_error_vector(n, V.base_ring(),\
                _random_error_position(n, number_errors))
        return message + error_vector
    
    def number_errors(self):
        r"""
        Returns the number of errors created by ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err = 3
            sage: Chan = channels.StaticErrorRateChannel(F, n_err)
            sage: Chan.number_errors()
            3
        """
        return self._number_errors










class ErrorErasureChannel(AbstractChannel):
    r"""
    Constructs a channel which adds errors to any message it transmits. It also erases several positions
    in the transmitted message. The output space of this channel is a cartesian product
    between its input space and a VectorSpace of the same dimension over GF(2)

    INPUT:

    - ``space`` -- the input and output space

    - ``number_errors`` -- the number of errors created in each transmitted
      message. It can be either an integer of a tuple. If an tuple is passed as
      an argument, the number of errors will be a random integer between the
      two bounds of this tuple.

    - ``number_erasures`` -- the number of erasures created in each transmitted
      message. It can be either an integer of a tuple. If an tuple is passed as an
      argument, the number of erasures will be a random integer between the
      two bounds of this tuple.

    EXAMPLES:

    We construct a ErrorErasureChannel which adds 2 errors
    and 2 erasures to any transmitted message::

        sage: F = VectorSpace(GF(59), 40)
        sage: n_err, n_era = 2, 2
        sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
        sage: Chan
        Error-and-erasure channel creating 2 error(s) and 2 erasure(s)

    We can also pass the number of errors and erasures as a couple of integers::

        sage: F = VectorSpace(GF(59), 40)
        sage: n_err, n_era = (1, 10), (1, 10)
        sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
        sage: Chan
        Error-and-erasure channel creating between 1 and 10 errors and between 1 and 10 erasures
    """

    def __init__(self, space, number_errors, number_erasures):
        r"""


        TESTS:

        If the sum of number of errors and number of erasures
        exceeds (or may exceed, in the case of tuples) the dimension of the input space,
        it will return an error::

            sage: F = VectorSpace(GF(59), 40)
            sage: n_err, n_era = 21, 21
            sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
            Traceback (most recent call last):
            ...
            ValueError: The total number of errors and erasures can exceed the dimension of the input space
        """
        output_space = CartesianProduct(space, VectorSpace(GF(2), space.dimension()))
        super(ErrorErasureChannel, self).__init__(space, output_space)
        no_err = number_errors if not hasattr(number_errors, "__iter__")\
                else number_errors[1]
        no_era = number_erasures if not hasattr(number_erasures, "__iter__")\
                else number_erasures[1]
        if no_err + no_era > space.dimension():
            raise ValueError("The total number of errors and erasures can exceed the dimension of the input space")
        self._number_errors = number_errors
        self._number_erasures = number_erasures

    def __repr__(self):
        r"""
        Returns a string representation of ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 50)
            sage: n_err, n_era = 21, 21
            sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
            sage: Chan
            Error-and-erasure channel creating 21 error(s) and 21 erasure(s)
        """
        if not hasattr(self.number_errors(), "__iter__"):
            return "Error-and-erasure channel creating %s error(s) and %s erasure(s)"\
                    %(self.number_errors(), self.number_erasures())
        else:
            no_err = self.number_errors()
            no_era = self.number_erasures()
            return "Error-and-erasure channel creating between %s and %s errors and between %s and %s erasures"\
            % (no_err[0], no_err[1], no_era[0], no_era[1])

    def _latex_(self):
        r"""
        Returns a latex representation of ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 50)
            sage: n_err, n_era = 21, 21
            sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
            sage: latex(Chan)
            \textnormal{Error-and-erasure channel creating 21 error(s) and 21 erasure(s)}
        """
        if not hasattr(self.number_errors(), "__iter__"):
            return "\\textnormal{Error-and-erasure channel creating %s error(s) and %s erasure(s)}"\
                    %(self.number_errors(), self.number_erasures())
        else:
            no_err = self.number_errors()
            no_era = self.number_erasures()
            return "\\textnormal{Error-and-erasure channel creating between %s and %s errors and between %s and %s erasures}"\
            % (no_err[0], no_err[1], no_era[0], no_era[1])

    def __eq__(self, other):
        r"""
        Checks if ``self`` is equal to ``other``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 50)
            sage: n_err = 17
            sage: n_era = 7
            sage: Chan1 = channels.ErrorErasureChannel(F, n_err, n_era)
            sage: Chan2 = channels.ErrorErasureChannel(F, n_err, n_era)
            sage: Chan1 == Chan2
            True
        """
        return isinstance(other, ErrorErasureChannel)\
                and self.input_space() == other.input_space()\
                and self.number_errors() == other.number_errors()\
                and self.number_erasures() == other.number_erasures()

    def transmit_unsafe(self, message):
        r"""
        Returns ``message`` with as many errors as ``self._number_errors`` in it, and as many erasures
        as ``self._number_erasures`` in it.
        If ``self._number_errors`` was passed as an tuple for the number of errors, it will
        pick a random integer between the bounds of the tuple and use it as the number of errors.
        The same method applies with ``self._number_erasures``.

        All erased positions are set to 0 in the transmitted message.
        It is guaranteed that the erasures and the errors will never overlap:
        the received message will always contains exactly as many errors and erasures
        as expected.

        This method does not check if ``message`` belongs to the input space of``self``.

        INPUT:

        - ``message`` -- a vector

        OUTPUT:

        - a couple of vectors, namely:

            - the transmitted message, which is ``message`` with erroneous and erased positions
            - the erasure vector, which contains ``1`` at the erased positions of the transmitted message
              , 0 elsewhere.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 11)
            sage: n_err, n_era = 2, 2
            sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
            sage: msg = F((3, 14, 15, 9, 26, 53, 58, 9, 7, 9, 3))
            sage: Chan.transmit_unsafe(msg) # random
            ((0, 14, 15, 0, 26, 53, 45, 9, 7, 14, 3), (1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0))
        """
        number_errors = _tuple_to_integer(self.number_errors())
        number_erasures = _tuple_to_integer(self.number_erasures())
        V = self.input_space()
        n = V.dimension()

        erroneous_positions = _random_error_position(n,\
                number_errors + number_erasures)
        error_split = _random_error_position(number_errors + number_erasures,\
                number_errors)
        error_positions = [ erroneous_positions[i] for i in\
                range(number_errors + number_erasures) if i in error_split ]
        erasure_positions = [ erroneous_positions[i] for i in\
                range(number_errors + number_erasures) if i not in error_split]

        error_vector = _random_error_vector(n, V.base_ring(), error_positions)
        erasure_vector = _random_error_vector(n , GF(2), erasure_positions)

        message = message + error_vector

        for i in erasure_positions:
            message[i] = 0
        return message, erasure_vector

    def number_errors(self):
        r"""
        Returns the number of errors created by ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err, n_era = 3, 0
            sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
            sage: Chan.number_errors()
            3
        """
        return self._number_errors

    def number_erasures(self):
        r"""
        Returns the number of erasures created by ``self``.

        EXAMPLES::

            sage: F = VectorSpace(GF(59), 6)
            sage: n_err, n_era = 0, 3
            sage: Chan = channels.ErrorErasureChannel(F, n_err, n_era)
            sage: Chan.number_erasures()
            3
        """
        return self._number_erasures
