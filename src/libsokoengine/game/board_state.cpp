#include "board_state.hpp"

#include <boost/algorithm/string.hpp>
#include <boost/lexical_cast.hpp>

using namespace std;

namespace sokoengine {
namespace game {

using io::Strings;

class LIBSOKOENGINE_LOCAL BoardState::PIMPL {
public:
  Positions m_pushers_positions;
  Positions m_boxes_positions;
  zobrist_key_t m_zobrist_hash;

  PIMPL(const Positions &pushers_positions, const Positions &boxes_positions,
        zobrist_key_t zobrist_hash)
      : m_pushers_positions(pushers_positions), m_boxes_positions(boxes_positions),
        m_zobrist_hash(zobrist_hash) {}

  PIMPL(const PIMPL &rv) = default;
  PIMPL &operator=(const PIMPL &rv) = default;
  PIMPL(PIMPL &&rv) = default;
  PIMPL &operator=(PIMPL &&rv) = default;
}; // BoardState::PIMPL

BoardState::BoardState(const Positions &pushers_positions,
                       const Positions &boxes_positions, zobrist_key_t zobrist_hash)
    : m_impl(make_unique<PIMPL>(pushers_positions, boxes_positions, zobrist_hash)) {}

BoardState::BoardState(const BoardState &rv) : m_impl(make_unique<PIMPL>(*rv.m_impl)) {}

BoardState &BoardState::operator=(const BoardState &rv) {
  if (this != &rv)
    m_impl = make_unique<PIMPL>(*rv.m_impl);
  return *this;
}

BoardState::BoardState(BoardState &&) = default;

BoardState &BoardState::operator=(BoardState &&) = default;

BoardState::~BoardState() = default;

bool BoardState::operator==(const BoardState &rv) const {
  return (m_impl->m_zobrist_hash != NO_HASH &&
          m_impl->m_zobrist_hash == rv.m_impl->m_zobrist_hash) ||
         (m_impl->m_pushers_positions == rv.m_impl->m_pushers_positions &&
          m_impl->m_boxes_positions == rv.m_impl->m_boxes_positions);
}

bool BoardState::operator!=(const BoardState &rv) const { return !(*this == rv); }

const Positions &BoardState::pushers_positions() const {
  return m_impl->m_pushers_positions;
}

Positions &BoardState::pushers_positions() { return m_impl->m_pushers_positions; }

const Positions &BoardState::boxes_positions() const {
  return m_impl->m_boxes_positions;
}

Positions &BoardState::boxes_positions() { return m_impl->m_boxes_positions; }

zobrist_key_t BoardState::zobrist_hash() const { return m_impl->m_zobrist_hash; }

zobrist_key_t &BoardState::zobrist_hash() { return m_impl->m_zobrist_hash; }

string BoardState::str() const {
  auto converter = [&](const Positions &v) {
    Strings retv;
    for (auto position : v)
      retv.push_back(boost::lexical_cast<string>(position));
    return retv;
  };

  return "<BoardState(pushers_positions=[" +
         boost::join(converter(m_impl->m_pushers_positions), ", ") + "],\n" +
         "            boxes_positions=[" +
         boost::join(converter(m_impl->m_boxes_positions), ", ") + "],\n" +
         "            zobrist_hash=" +
         boost::lexical_cast<string>(m_impl->m_zobrist_hash) + ">";
}

string BoardState::repr() const {
  auto converter = [&](const Positions &v) {
    Strings retv;
    for (auto position : v)
      retv.push_back(boost::lexical_cast<string>(position));
    return retv;
  };

  return "BoardState(pushers_positions=[" +
         boost::join(converter(m_impl->m_pushers_positions), ", ") + "], " +
         "boxes_positions=[" + boost::join(converter(m_impl->m_boxes_positions), ", ") +
         "], " + "zobrist_hash=" + boost::lexical_cast<string>(m_impl->m_zobrist_hash) +
         ")";
}

} // namespace game
} // namespace sokoengine
