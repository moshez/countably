Getting Started with countably
==============================

``countably`` is a library for lazy, immutable, (often) infinite sequences of
numbers. You describe a sequence with arithmetic and slicing; nothing is
computed until you ask for it.

The primitives
--------------

There are only two:

* :func:`countably.constant` -- an infinite sequence whose every element is the
  same number.
* :func:`countably.count` -- the infinite sequence ``0, 1, 2, 3, ...``.

.. code-block:: python

    from countably import constant, count

    sevens = constant(7)            # 7, 7, 7, 7, ...
    naturals = count()              # 0, 1, 2, 3, ...

Everything else is built from these two by arithmetic, comparisons,
rounding, slicing, and the helpers :func:`countably.maximum` /
:func:`countably.minimum`.

Arithmetic and number coercion
------------------------------

All the usual operators apply element-wise. Plain numbers on the left or
right are automatically coerced into a :func:`constant`, so you don't have
to wrap them yourself:

.. code-block:: python

    odds = 2 * count() + 1           # 1, 3, 5, 7, ...
    evens = 2 * count()              # 0, 2, 4, 6, ...
    reciprocals = 1 / (count() + 1)  # 1, 0.5, 1/3, 1/4, ...
    squares = count() ** 2           # 0, 1, 4, 9, 16, ...
    halved = count() // 2            # 0, 0, 1, 1, 2, 2, ...
    cycle = count() % 3              # 0, 1, 2, 0, 1, 2, ...

Comparisons
-----------

The comparison operators (``<``, ``<=``, ``>``, ``>=``) return sequences of
booleans. Since ``bool`` is a number, those are themselves
``NumberSequence`` objects you can keep computing with:

.. code-block:: python

    big_enough = count() >= 5        # F, F, F, F, F, T, T, T, ...

Element-wise ``max`` and ``min``
--------------------------------

Python's built-in :func:`max` / :func:`min` need a single ``bool`` from
comparison, which sequences don't supply. Use the module-level helpers
instead:

.. code-block:: python

    from countably import maximum, minimum

    clamped_low = maximum(count(), 3)        # 3, 3, 3, 3, 4, 5, 6, ...
    clamped_high = minimum(count(), 3)       # 0, 1, 2, 3, 3, 3, 3, ...

Both arguments may be sequences; the result has the length of the shorter
one.

Slicing
-------

Slicing is lazy and produces another sequence. Infinite slices stay
infinite; finite slices have a real ``len()``:

.. code-block:: python

    every_third = count()[2::3]              # 2, 5, 8, 11, ...  (infinite)
    small_window = count()[2:10]             # length 8, finite
    even_step = count()[0:20:2]              # length 10, finite

When two sequences of different length combine, the result uses the
shorter length:

.. code-block:: python

    short = count()[0:5]                     # length 5
    sum_with_infinite = short + count()      # length 5

Rounding, floor, ceil, trunc
----------------------------

Sequences cooperate with the standard rounding functions:

.. code-block:: python

    import math
    half_steps = count() / 2
    math.floor(half_steps)                   # 0, 0, 1, 1, 2, 2, ...
    math.ceil(half_steps)                    # 0, 1, 1, 2, 2, 3, ...
    round(half_steps)                        # banker's rounding
    round(count() / 3, 2)                    # round to 2 dp

Fibonacci, in one expression
----------------------------

Binet's formula plus rounding gives the Fibonacci sequence directly --
no recursion, no state:

.. code-block:: python

    import math
    from countably import count

    phi = (1 + math.sqrt(5)) / 2
    fib = round(phi ** count() / math.sqrt(5))

    print(fib)
    # [0, 1, 1, 2, 3, ....]

    list(fib[:12])
    # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

(Valid for ``n`` up to ~70 before floating-point precision gives out.)

Patterns to avoid
-----------------

* ``bool(seq)`` raises :class:`TypeError`: the truth value of a (possibly
  infinite) sequence is undefined. The same goes for ``if seq: ...``.
* ``list(count())`` and ``for x in count(): ...`` never terminate.
  Always slice or :func:`itertools.islice` first.
* Negative indices work on *finite* slices (``seq[2:10][-1]``) but not on
  infinite sequences.

What's next
-----------

See the :doc:`api-reference` for the full surface, including the
:class:`countably.NumberSequence` protocol.
