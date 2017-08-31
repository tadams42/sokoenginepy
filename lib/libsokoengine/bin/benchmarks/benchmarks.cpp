#include <sokoengine.hpp>

#include <string>
#include <chrono>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <sstream>
#include <numeric>

using namespace std;
using namespace std::chrono;

namespace sokoengine {
  namespace benchmarks {

class BoardType {
public:
  enum EBoardType {
    SMALL, LARGE
  };

  BoardType(EBoardType which) : m_board_type(which) {}

  SokobanBoard board() const {
    if (m_board_type == SMALL) {
      return SokobanBoard(string() +
        "##########\n" +
        "#      **#\n" +
        "#      **#\n" +
        "# *@   **#\n" +
        "#      **#\n" +
        "##########\n"
      );
    } else {
      return SokobanBoard(string() +
        "######################################\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#*************          *************#\n" +
        "#*************          *************#\n" +
        "#*************          *************#\n" +
        "#*************    *@    *************#\n" +
        "#*************          *************#\n" +
        "#*************          *************#\n" +
        "#*************          *************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "#************************************#\n" +
        "######################################\n"
      );
    }
  }

private:
  EBoardType m_board_type = EBoardType::SMALL;
};


class BenchmarkType {
public:
  enum EBenchmarkType {
    FORWARD_MOVER, REVERSE_MOVER
  };

  BenchmarkType(EBenchmarkType which) : m_type(which) {}

  bool is_reverse() const {
    return m_type == REVERSE_MOVER;
  }

  string title() const {
    if (m_type == FORWARD_MOVER) {
      return "Forward mover";
    }
    return "Reverse mover";
  }

  Direction direction() const {
    if (m_type == FORWARD_MOVER) {
      return Direction::LEFT;
    } else {
      return Direction::RIGHT;
    }
  }

private:
  EBenchmarkType m_type = EBenchmarkType::FORWARD_MOVER;
};


class MovementBenchmark {
  double m_miliseconds_used = 0;
  BoardType m_board_type;
  BenchmarkType m_benchmark_type;
  size_t m_moves_count = 0;
  SokobanBoard m_board = m_board_type.board();
  Mover m_mover = Mover(
    m_board,
    m_benchmark_type.is_reverse() ? SolvingMode::REVERSE : SolvingMode::FORWARD
  );

public:
  MovementBenchmark(BoardType board_type, BenchmarkType benchmark_type,
                    size_t moves_count):
    m_board_type(board_type),
    m_benchmark_type(benchmark_type),
    m_moves_count(moves_count),
    m_board(board_type.board()),
    m_mover(
      m_board,
      benchmark_type.is_reverse() ? SolvingMode::REVERSE : SolvingMode::FORWARD
    )
  {}

  double miliseconds_used() const {
    return m_miliseconds_used;
  }

  double moves_per_second() const {
    return m_moves_count / (m_miliseconds_used / 1000);
  }

  void run() {
    m_miliseconds_used = 0;
    high_resolution_clock::time_point start_time, end_time;
    bool undo_move = false;

    for (auto i = 0; i < m_moves_count; i++) {
      if (undo_move) {
        start_time = std::chrono::high_resolution_clock::now();
        m_mover.undo_last_move();
        end_time = std::chrono::high_resolution_clock::now();
        m_miliseconds_used += duration_cast<duration<double>>(
          end_time - start_time
        ).count();
        undo_move = false;
      } else {
        start_time = std::chrono::high_resolution_clock::now();
        m_mover.move(m_benchmark_type.direction());
        end_time = std::chrono::high_resolution_clock::now();
        m_miliseconds_used += duration_cast<duration<double>>(
          end_time - start_time
        ).count();
        undo_move = true;
      }
    }

    m_miliseconds_used = m_miliseconds_used * 1000;
  }
};


class MovementBenchmarkPrinter {
  size_t m_runs_count;
  size_t m_moves_per_run_count;
public:

  MovementBenchmarkPrinter(size_t runs_count, size_t moves_per_run_count):
    m_runs_count(runs_count),
    m_moves_per_run_count(moves_per_run_count)
  {}

  string board_header(const BoardType& board_type) const {
    SokobanBoard board = board_type.board();
    BoardState state(board);
    ostringstream ss;
    ss << setw(10) << left << "SokobanBoard: "
      << "W: " << setw(5) << left << board.width()
      << "H: " << setw(5) << left << board.height()
      << "P: " << setw(5) << left << state.pushers_count()
      << "B: " << setw(5) << left << state.boxes_count();
    return ss.str();
  }

  double run_and_print_experiment(
    const BoardType& board_type, const BenchmarkType& benchmark_type,
    double pivot_speed = 0
  ) {
    std::deque<double> speeds;
    std::deque<double> times;

    cout << setw(20) << benchmark_type.title() << ": " << flush;

    for (size_t i = 0; i < m_runs_count; ++i) {
      MovementBenchmark benchmarker(
        board_type, benchmark_type, m_moves_per_run_count
      );
      benchmarker.run();
      speeds.push_back(benchmarker.moves_per_second());
      times.push_back(benchmarker.miliseconds_used());
      cout << '.' << flush;
    }

    double mean_speed = accumulate(speeds.cbegin(), speeds.cend(), 0.0) / speeds.size();
    double mean_time = accumulate(times.cbegin(), times.cend(), 0.0) / times.size();

    cout << " " <<
      setprecision(2) << scientific <<
      mean_time << " [ms] " <<
      setprecision(2) << scientific <<
      mean_speed << " [moves/s]" <<
      flush;

    if (pivot_speed > 0) {
      cout << "   " <<
        setprecision(2) << fixed <<
        mean_speed / pivot_speed * 100 <<
        "%" << endl;
    } else {
      cout << "   " << "100.00%" << endl;
    }

    return mean_speed;
  }

  static void run_all() {
    cout << "--------------------------------------------------" << endl;
    cout << "--              MOVER BENCHMARKS                --" << endl;
    cout << "--------------------------------------------------" << endl << endl;
    size_t runs = 5;
    size_t moves_per_run = 3e6;

    double pivot_speed = 3e6;

    MovementBenchmarkPrinter printer(runs, moves_per_run);

    cout << printer.board_header(BoardType(BoardType::SMALL)) << endl;

    printer.run_and_print_experiment(
      BoardType(BoardType::SMALL), BenchmarkType(BenchmarkType::FORWARD_MOVER),
      pivot_speed
    );

    printer.run_and_print_experiment(
      BoardType(BoardType::SMALL), BenchmarkType(BenchmarkType::REVERSE_MOVER),
      pivot_speed
    );
  }
};

  } //namespace benchmarks
} // namespace sokoengine


int main() {
  using namespace sokoengine;
  using namespace sokoengine::benchmarks;

  MovementBenchmarkPrinter::run_all();

  return 0;
}
