import asyncio


class _Sentinel:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


_NONE = _Sentinel()


def _is_none(v):
    return v.__class__ is _Sentinel


class _Bool:
    def __init__(self, raw):
        self._raw = raw

    def is_true(self):
        return self._raw

    def is_false(self):
        return not self._raw

    def to_int(self):
        return 1 if self._raw else 0

    @staticmethod
    def true():
        return _Bool(True)

    @staticmethod
    def false():
        return _Bool(False)


class _Pair:
    def __init__(self, first, second):
        self._first  = first
        self._second = second

    def first(self):
        return self._first

    def second(self):
        return self._second


class _Thunk:
    def __init__(self, fn, *args):
        self._fn   = fn
        self._args = args

    def force(self):
        return self._fn(*self._args)


def _trampoline(thunk):
    result = thunk
    while result.__class__ is _Thunk:
        result = result.force()
    return result


class _Node:
    def __init__(self, value, next_node=None):
        self.value     = value
        self.next_node = next_node if next_node is not None else _NONE


class _LinkedList:
    def __init__(self):
        self.head = _NONE

    def _append_recursive(self, node, value):
        if _is_none(node.next_node):
            node.next_node = _Node(value)
            return
        self._append_recursive(node.next_node, value)

    def append(self, value):
        if _is_none(self.head):
            self.head = _Node(value)
        else:
            self._append_recursive(self.head, value)

    def _iter_recursive(self, node):
        if _is_none(node):
            return
        yield node.value
        yield from self._iter_recursive(node.next_node)

    def __iter__(self):
        return self._iter_recursive(self.head)

    def _len_recursive(self, node, acc):
        if _is_none(node):
            return acc
        return self._len_recursive(node.next_node, acc + _Bool.true().to_int())

    def __len__(self):
        return self._len_recursive(self.head, _Bool.false().to_int())


class _CharList:
    def __init__(self):
        self._ll = _LinkedList()

    def append_char(self, c):
        self._ll.append(c)

    def _concat_recursive(self, node, result):
        if _is_none(node):
            return result
        result.append_char(node.value)
        return self._concat_recursive(node.next_node, result)

    def concat(self, other):
        result = _CharList()
        self._concat_recursive(self._ll.head, result)
        other._concat_recursive(other._ll.head, result)
        return result

    def _to_str_recursive(self, node, acc):
        if _is_none(node):
            return acc
        return self._to_str_recursive(node.next_node, acc + [node.value])

    def to_str(self):
        return "".join(self._to_str_recursive(self._ll.head, []))

    @staticmethod
    def from_char(c):
        cl = _CharList()
        cl.append_char(c)
        return cl


class MakeStar:
    def __init__(self, max_stars):
        self.max_stars = max_stars

    def _zero(self):
        return _Bool.false().to_int()

    def _one(self):
        return _Bool.true().to_int()

    def _intUnary(self, n):
        acc       = _LinkedList()
        remaining = n
        while remaining != self._zero():
            acc.append(self._one())
            remaining = remaining - self._one()
        return acc

    def _unrayInt(self, unary):
        acc  = self._zero()
        node = unary.head
        while not _is_none(node):
            acc  = acc + node.value
            node = node.next_node
        return acc

    def _san(self, n):
        return self._unrayInt(self._intUnary(n))

    def _raw_equal(self, a, b):
        diff = self._unary_add(self._unary_subtract(a, b), self._unary_subtract(b, a))
        if self._san(diff) - self._zero() == self._zero():
            return _Bool.true()
        return _Bool.false()

    def _unary_gte(self, a, b):
        a_node = self._intUnary(a).head
        b_node = self._intUnary(b).head
        while not _is_none(b_node):
            if _is_none(a_node):
                return _Bool.false()
            a_node = a_node.next_node
            b_node = b_node.next_node
        return _Bool.true()
    #day1
    def _ll_cr(self, node, target):
        if _is_none(node):
            return
        target.append(node.value)
        self._ll_cr(node.next_node, target)

    def _ll_concat(self, a, b):
        result = _LinkedList()
        self._ll_cr(a.head, result)
        self._ll_cr(b.head, result)
        return result

    def _unary_add(self, a, b):
        return self._san(
            self._unrayInt(self._ll_concat(self._intUnary(a), self._intUnary(b)))
        )

    def _ll_dor(self, node, acc, skipped):
        if _is_none(node):
            return acc
        if skipped.is_true():
            acc.append(node.value)
        return self._ll_dor(node.next_node, acc, _Bool.true())

    def _ll_do(self, ll):
        return self._ll_dor(ll.head, _LinkedList(), _Bool.false())

    def _unary_subtract(self, a, b):
        result = self._intUnary(a)
        count  = self._san(b)
        while count != self._zero():
            if _is_none(result.head):
                return self._zero()
            result = self._ll_do(result)
            count  = count - self._one()
        return self._san(self._unrayInt(result))

    def _mr(self, a_node, b, acc):
        if _is_none(a_node):
            return acc
        return self._mr(a_node.next_node, b, self._ll_concat(acc, b))

    def _mvu(self, a, b):
        result = self._mr(
            self._intUnary(a).head,
            self._intUnary(b),
            _LinkedList()
        )
        return self._san(self._unrayInt(result))

    def _unary_div_recursive(self, remaining, divisor, quotient):
        if self._unary_gte(remaining, divisor).is_false():
            return self._san(quotient)
        return self._unary_div_recursive(
            self._unary_subtract(remaining, divisor),
            divisor,
            self._unary_add(quotient, self._one())
        )

    def _unary_div(self, a, b):
        return self._unary_div_recursive(self._san(a), self._san(b), self._zero())

    def _unary_mod_recursive(self, remaining, divisor):
        if self._unary_gte(remaining, divisor).is_false():
            return self._san(remaining)
        return self._unary_mod_recursive(self._unary_subtract(remaining, divisor), divisor)

    def _unary_mod(self, a, b):
        return self._unary_mod_recursive(self._san(a), self._san(b))

    def _power_of_two_recursive(self, n_node, acc):
        if _is_none(n_node):
            return self._san(acc)
        return self._power_of_two_recursive(
            n_node.next_node,
            self._mvu(acc, self._two())
        )

    def _p_two(self, n):
        return self._power_of_two_recursive(self._intUnary(n).head, self._one())

    def _urr(self, remaining, current, acc):
        if self._raw_equal(remaining, self._zero()).is_true():
            return acc
        acc.append(self._san(current))
        return self._urr(
            self._unary_subtract(remaining, self._one()),
            self._unary_add(current, self._one()),
            acc
        )

    def _ur(self, n):
        return self._urr(n, self._zero(), _LinkedList())

    def _uer(self, node, counter, acc):
        if _is_none(node):
            return acc
        acc.append(_Pair(self._san(counter), node.value))
        return self._uer(
            node.next_node,
            self._unary_add(counter, self._one()),
            acc
        )

    def _ue(self, ll):
        return self._uer(ll.head, self._zero(), _LinkedList())

    def _ll_gr(self, node, idx, current):
        if _is_none(node):
            return self._zero()
        if self._raw_equal(current, idx).is_true():
            return node.value
        return self._ll_gr(
            node.next_node,
            idx,
            self._unary_add(current, self._one())
        )

    def _ll_get(self, ll, idx):
        return self._ll_gr(ll.head, idx, self._zero())

    def _ll_rr(self, node, acc):
        if _is_none(node):
            return acc
        new_acc = _LinkedList()
        new_acc.append(node.value)
        self._ll_cr(acc.head, new_acc)
        return self._ll_rr(node.next_node, new_acc)

    def _ll_r(self, ll):
        return self._ll_rr(ll.head, _LinkedList())

    def _two(self):
        return self._san(self._unary_add(self._one(), self._one()))

    def _three(self):
        return self._san(self._unary_add(self._two(), self._one()))

    def _four(self):
        return self._san(self._mvu(self._two(), self._two()))

    def _five(self):
        return self._san(self._unary_add(self._four(), self._one()))

    def _six(self):
        return self._san(self._mvu(self._three(), self._two()))

    def _seven(self):
        return self._san(self._unary_add(self._six(), self._one()))

    def _fortyTwo(self):
        return self._san(self._mvu(self._six(), self._seven()))

    def _ptwo(self):
        return self._san(self._p_two(self._seven()))

    def _pto(self):
        return self._san(self._p_two(self._six()))

    def _ptt(self):
        return self._san(self._p_two(self._five()))

    def _ptth(self):
        return self._san(self._p_two(self._four()))

    def _ptf(self):
        return self._san(self._p_two(self._three()))

    def _ptff(self):
        return self._san(self._p_two(self._two()))

    def _pts(self):
        return self._san(self._p_two(self._one()))

    def _ptse(self):
        return self._san(self._p_two(self._zero()))


    def _get_all_powers_of_two(self):
        ll = _LinkedList()
        ll.append(self._ptwo())
        ll.append(self._pto())
        ll.append(self._ptt())
        ll.append(self._ptth())
        ll.append(self._ptf())
        ll.append(self._ptff())
        ll.append(self._pts())
        ll.append(self._ptse())
        return ll

    #합치는거부터
    def _gbp(self, position_power):
        return self._san(self._unary_mod(
            self._unary_div(self._fortyTwo(), position_power),
            self._two()
        ))

    def _ft(self):
        return self._gbp(self._ptwo())

    def _fto(self):
        return self._gbp(self._pto())

    def _ftt(self):
        return self._gbp(self._ptt())

    def _ftth(self):
        return self._gbp(self._ptth())

    def _fttf(self):
        return self._gbp(self._ptf())

    def _fttff(self):
        return self._gbp(self._ptff())

    def _ftts(self):
        return self._gbp(self._pts())

    def _fttse(self):
        return self._gbp(self._ptse())

    def _getFT(self):
        ll = _LinkedList()
        ll.append(self._ft())
        ll.append(self._fto())
        ll.append(self._ftt())
        ll.append(self._ftth())
        ll.append(self._fttf())
        ll.append(self._fttff())
        ll.append(self._ftts())
        ll.append(self._fttse())
        return ll

    def _makestar(self, bits_enum_node, powers, code):
        if _is_none(bits_enum_node):
            return self._san(code)
        pair      = bits_enum_node.value
        bit_idx   = pair.first()
        bit_val   = pair.second()
        power_val = self._ll_get(powers, bit_idx)
        term      = self._mvu(self._san(bit_val), self._san(power_val))
        return self._makestar(
            bits_enum_node.next_node,
            powers,
            self._unary_add(code, term)
        )
    #별이 아니라 공백으로 가득차던데 내일 확인해봐야할듯
    def _getStar(self):
        bits   = self._getFT()
        powers = self._get_all_powers_of_two()
        return self._makestar(
            self._ue(bits).head,
            powers,
            self._zero()
        )

    def _findStarC(self, candidate_code, target_code):
        if self._raw_equal(self._san(candidate_code), target_code).is_true():
            return _CharList.from_char(chr(self._san(candidate_code)))
        return _Thunk(
            self._findStarC,
            self._unary_add(candidate_code, self._one()),
            target_code
        )

    def _getStarC(self):
        target_code = self._getStar()
        return _trampoline(_Thunk(self._findStarC, self._zero(), target_code))

    def _buildStarL(self, n_node, acc):
        if _is_none(n_node):
            return acc
        acc.append(self._getStarC())
        return self._buildStarL(n_node.next_node, acc)

    def _joinCList(self, node, acc):
        if _is_none(node):
            return acc
        return self._joinCList(node.next_node, acc.concat(node.value))
    
    def _rstar(self, count):
        star_list   = self._buildStarL(
            self._intUnary(self._san(count)).head,
            _LinkedList()
        )
        star_list    = self._ll_r(self._ll_r(star_list))
        joined_once  = self._joinCList(star_list.head, _CharList())
        split_again  = _LinkedList()
        for c in joined_once.to_str():
            split_again.append(_CharList.from_char(c))
        split_again  = self._ll_r(self._ll_r(split_again))
        joined_twice = self._joinCList(split_again.head, _CharList())
        return joined_twice.to_str()

    async def ssm(self, count):
        return self._rstar(count)

    async def finish(self):
        one        = self._one()
        max_stars  = self._san(self.max_stars)
        all_counts = self._ll_do(
            self._ur(self._unary_add(max_stars, one))
        )
        tasks   = [self.ssm(i) for i in all_counts]
        results = await asyncio.gather(*tasks)
        for cosmic_dust in results:
            print(cosmic_dust)


if __name__ == "__main__":
    five = MakeStar(_Bool.true().to_int())._five()
    asyncio.run(MakeStar(five).finish())