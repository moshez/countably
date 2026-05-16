countably
=========

Lazy, immutable, infinite numeric sequences for Python.

``countably`` lets you describe sequences declaratively, the way you'd
write them on paper, and evaluate them on demand:

.. code-block:: python

    from countably import count, constant

    triangular = count() * (count() + 1) // 2     # 0, 1, 3, 6, 10, ...
    powers_of_two = 2 ** count()                  # 1, 2, 4, 8, 16, ...
    every_third = count()[2::3]                   # 2, 5, 8, 11, ...

The primitives are just :func:`constant` and :func:`count`. Arithmetic,
comparisons, slicing, and element-wise :func:`maximum` / :func:`minimum`
build everything else. Plain numbers are coerced automatically, so
``3 + 5 * count()`` is equivalent to ``constant(3) + constant(5) * count()``.

Highlights
----------

* **Lazy** -- elements are computed only on access, with a per-instance
  100-item LRU cache for random access. Iteration walks the inputs
  directly, bypassing the cache.
* **Immutable** -- every operation produces a new sequence; nothing is
  mutated.
* **Iterable, not iterator** -- ``iter(seq)`` starts fresh every time.
* **Slices are lazy too** -- ``seq[2::3]`` stays infinite, ``seq[2:10]``
  is finite with a real ``len()``. Arithmetic between sequences uses the
  shorter length.
* **Round / floor / ceil / trunc** are supported through the standard
  Python protocols (``math.floor(seq)``, ``round(seq)``).
* **Comparisons** (``<``, ``<=``, ``>``, ``>=``) return sequences of
  booleans, which are numbers in the same world.

See ``doc/quick-start.rst`` for usage including a Fibonacci one-liner.

Install
-------

.. code-block:: bash

    pip install countably
