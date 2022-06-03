#include "rle.hpp"
#include "utilities.hpp"

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <sstream>

using namespace std;

namespace sokoengine {
namespace io {
namespace implementation {

class LIBSOKOENGINE_LOCAL RLE {
  // TODO: Rewrite this whole monstrosity using Boost.Spirit

  // Assumes @a line was checked with check_groups.
  // @todo Implemented recursively, could that be changed?
  bool decode_with_groups(string &line) const {
    bool retv;

    string::const_iterator gr_beg, gr_end, i, iend;
    string tmp, dest;

    i = line.begin();
    iend = line.end();
    do {
      gr_beg = group_begin(i, iend);

      if (gr_beg != iend) {
        // handle non grouped part
        tmp.append(i, gr_beg);
        retv = decode_token(tmp);

        // handle grouped part
        if (retv) {
          dest += tmp;
          tmp.clear();
          // find grouped part
          gr_end = group_end(gr_beg, iend);
          i = gr_end; // fixing i for next iteration
          if (i != iend) { ++i; }
          // handle grouped part
          string::size_type nr_groups = extract_beginning_digits(gr_beg, gr_end);
          if (nr_groups == 0) { nr_groups = 1; }
          gr_beg = find(gr_beg, gr_end, m_left_delimiter);
          tmp.append(gr_beg + 1, gr_end);
          retv = decode_with_groups(tmp);
          if (retv) {
            tmp.insert(tmp.begin(), m_left_delimiter);
            tmp += m_right_delimiter;
            for (string::size_type j = 0; j < nr_groups; ++j) {
              dest.append(tmp);
            }
          }
          tmp.clear();
        }
      } else { // handle last non grouped part
        tmp.insert(tmp.end(), i, iend);
        retv = decode_token(tmp);
        dest += tmp;
        tmp.clear();
        i = iend; // we're done
      }
    } while (i != iend);

    if (retv) { line = dest; }
    return retv;
  }

  bool decode_token(string &to_decode) const {
    // Condition also includes situation where input consists exclusively from
    // digits
    bool ends_with_digit = to_decode.empty() ? false : isdigit(to_decode.back()) != 0;

    if (ends_with_digit) return false;

    if (is_blank(to_decode)) return true;

    if (any_of(to_decode.begin(), to_decode.end(),
               [](char c) { return isdigit(c) != 0; })) {
      istringstream instr;
      noskipws(instr);
      instr.str(to_decode);
      to_decode.clear();

      string::size_type nr_chars;
      while (instr) {
        char c = static_cast<char>(instr.peek());
        if (!instr.eof()) {
          if (isdigit(c)) {
            instr >> nr_chars;
            instr >> c;
            to_decode.insert(to_decode.end(), nr_chars, c);
          } else {
            instr >> c;
            to_decode += c;
          }
        }
      }
    }
    return true;
  }

  // Returns true if
  //   - groups are properly opened and closed
  //   - groups don't exist
  bool check_groups(const string &line) const {
    string::const_iterator first_left, first_right;
    string::const_reverse_iterator last_left, last_right;
    first_left = find(line.begin(), line.end(), m_left_delimiter);
    first_right = find(line.begin(), line.end(), m_right_delimiter);
    last_left = find(line.rbegin(), line.rend(), m_left_delimiter);
    last_right = find(line.rbegin(), line.rend(), m_right_delimiter);

    string::const_iterator::difference_type dist_fleft, dist_fright, dist_lleft,
      dist_lright;
    dist_fleft = distance(line.begin(), first_left);
    dist_fright = distance(line.begin(), first_right);
    dist_lleft = distance(line.rbegin(), last_left);
    dist_lright = distance(line.rbegin(), last_right);

    bool begin_ok = (dist_fleft < dist_fright) ||
                    (first_left == line.end() && first_right == line.end());

    bool end_ok = (dist_lleft > dist_lright) ||
                  (last_left == line.rend() && last_right == line.rend());

    string::difference_type ld = count(line.begin(), line.end(), m_left_delimiter);
    string::difference_type rd = count(line.begin(), line.end(), m_right_delimiter);

    bool count_ok = ld == rd;

    return begin_ok && end_ok && count_ok;
  }

  // Marks beginning of RLE group (digits before beginning delimiter are also
  // detected).
  string::const_iterator group_begin(string::const_iterator from,
                                     string::const_iterator str_end) const {
    string::const_iterator retv;

    retv = find(from, str_end, m_left_delimiter);

    if (retv != str_end) {
      bool non_digit_found = false;
      if (retv != from) { --retv; }
      do {
        if (isdigit(*retv)) {
          if (retv != from) { --retv; }
        } else {
          if (*retv != m_left_delimiter) { ++retv; }
          non_digit_found = true;
        }
      } while (retv != from && !non_digit_found);
    }
    return retv;
  }

  // Returns iterator pointing to group end of current group. Assumes string
  // was checked with check_groups
  string::const_iterator group_end(string::const_iterator gr_begin,
                                   string::const_iterator str_end) const {
    string::const_iterator i, retv = str_end;
    string::difference_type nesting_lvl = 0;
    i = find(gr_begin, str_end, m_left_delimiter);
    // we can assume that there is no right delimiter before
    // first left one because string was checked with check_groups
    if (i != str_end) {
      nesting_lvl = 1;
      ++i;
    }
    for (; i != str_end && nesting_lvl != 0; ++i) {
      if (*i == m_left_delimiter) {
        nesting_lvl++;
      } else if (*i == m_right_delimiter) {
        nesting_lvl--;
      }
      if (nesting_lvl == 0) { retv = i; }
    }
    return retv;
  }

  string::size_type extract_beginning_digits(string::const_iterator str_beg,
                                             string::const_iterator str_end) const {
    string::size_type retv = 0;
    string tmp;

    bool non_digit_found;
    if (str_beg != str_end) {
      non_digit_found = !isdigit(*str_beg);
    } else {
      non_digit_found = true;
    }

    for (; str_beg != str_end && !non_digit_found; ++str_beg) {
      non_digit_found = !isdigit(*str_beg);
      if (!non_digit_found) { tmp += *str_beg; }
    }

    if (!tmp.empty()) { retv = stoul(tmp); }
    return retv;
  }

  char m_left_delimiter;
  char m_right_delimiter;

public:
  bool encode(string &to_encode) {
    if (any_of(to_encode.begin(), to_encode.end(), [](char c) { return isdigit(c); })) {
      return false;
    }
    if (to_encode.empty()) { return true; }
    string::size_type found = 0, nextfound = 0;
    ostringstream oss;
    nextfound = to_encode.find_first_not_of(to_encode[found], found);
    while (nextfound != string::npos) {
      if (nextfound - found > 1) { oss << nextfound - found; }
      oss << to_encode[found];
      found = nextfound;
      nextfound = to_encode.find_first_not_of(to_encode[found], found);
    }
    if (to_encode.length() - found > 1) { oss << to_encode.length() - found; }
    oss << to_encode[found];
    to_encode = oss.str();
    return true;
  }

  // Decodes RLE string.
  //   - supports grouped entities with delimiters being '(' and ')'
  //   - groups can be nested
  //   - group delimiters are discarded from decoded string
  //
  // Fails if:
  //   - badly formed RLE string (ending with digit or contains only digits)
  //   - badly formed groups
  //
  // In case of failure input is not modified.
  bool decode(string &input) {
    m_left_delimiter = Rle::GROUP_START;
    m_right_delimiter = Rle::GROUP_END;

    bool retv = false;
    if (check_groups(input)) { retv = decode_with_groups(input); }

    if (retv) {
      input.erase(
        remove_if(input.begin(), input.end(),
                  [](char c) { return c == Rle::GROUP_START || c == Rle::GROUP_END; }),
        input.end());
      replace(input.begin(), input.end(), static_cast<char>(Rle::EOL), '\n');
    }
    return retv;
  }
};

///
/// RLE encodes string.
///
///   - "aaabbbb"                       -> "3a4b"
///   - "aabbbbccddeeeeffddeeeeff"      -> "2a4b2c2d4e2f2d4e2f"
///   - "aabbbbccddee\neeffddeeeeff"    -> "2a4b2c2d2e|2e2f2d4e2f"
///   - "aabbbbccddee     eeffddeeeeff" -> "2a4b2c2d2e5 2e2f2d4e2f
///
string Rle::encode(const string &src) {
  implementation::RLE rle;

  string data = src;
  replace(data.begin(), data.end(), '\n', Rle::EOL);
  rle.encode(data);

  return data;
}

///
/// Decodes RLE encoded string.
///
/// Supports RLE groups, ie strings like:
///
///   - "3(a2b)4b"               -> ["abbabbabbbbbb"]
///
/// Returns a list of RLE decoded lines:
///
///   - "2a4b2c2d2e|2e2f2d4e2f"  -> ["aabbbbccddee", "eeffddeeeeff"]
///
string Rle::decode(const string &src) {
  implementation::RLE rle;

  string data = src;
  rle.decode(data);

  return data;
}

} // namespace implementation
} // namespace io
} // namespace sokoengine
