#include "sokoenginepyext.hpp"

#include <sstream>

using sokoengine::game::Tessellation;
using sokoengine::io::Collection;
using sokoengine::io::Puzzles;
using std::istream;
using std::istringstream;
using std::ostream;
using std::ostringstream;
using std::string;
using std::filesystem::path;

void stream_load(Collection &self, py::object &stream, Tessellation tessellation_hint);
void stream_dump(const Collection &self, py::object &stream);

void export_io_collection(py::module &m) {
  auto pyCollection = py::class_<Collection>(m, "Collection");

  pyCollection.def(
    py::init<string, string, string, string, string>(),
    py::arg("title")      = "",
    py::arg("author")     = "",
    py::arg("created_at") = "",
    py::arg("updated_at") = "",
    py::arg("notes")      = ""
  );

  pyCollection.def_property(
    "title",
    [](const Collection &self) {
      return self.title();
    },
    [](Collection &self, const string &rv) {
      self.title() = rv;
    }
  );

  pyCollection.def_property(
    "author",
    [](const Collection &self) {
      return self.author();
    },
    [](Collection &self, const string &rv) {
      self.author() = rv;
    }
  );

  pyCollection.def_property(
    "notes",
    [](const Collection &self) {
      return self.notes();
    },
    [](Collection &self, const string &rv) {
      self.notes() = rv;
    }
  );

  pyCollection.def_property(
    "created_at",
    [](const Collection &self) {
      return self.created_at();
    },
    [](Collection &self, const string &rv) {
      self.created_at() = rv;
    }
  );

  pyCollection.def_property(
    "updated_at",
    [](const Collection &self) {
      return self.updated_at();
    },
    [](Collection &self, const string &rv) {
      self.updated_at() = rv;
    }
  );

  pyCollection.def_property(
    "puzzles",
    [](const Collection &self) {
      return self.puzzles();
    },
    [](Collection &self, const Puzzles &rv) {
      self.puzzles() = rv;
    }
  );

  pyCollection
    .def(
      "load",
      py::overload_cast<const path &, Tessellation>(&Collection::load),
      py::arg("src").none(false),
      py::arg("tessellation_hint") = Tessellation::SOKOBAN
    )
    .def(
      "load",
      py::overload_cast<const string &, Tessellation>(&Collection::load),
      py::arg("src").none(false),
      py::arg("tessellation_hint") = Tessellation::SOKOBAN
    )
    .def(
      "load",
      py::overload_cast<Collection &, py::object &, Tessellation>(&stream_load),
      py::arg("src").none(false),
      py::arg("tessellation_hint") = Tessellation::SOKOBAN
    );

  pyCollection.def(
    "loads",
    py::overload_cast<const string &, Tessellation>(&Collection::loads),
    py::arg("data").none(false),
    py::arg("tessellation_hint") = Tessellation::SOKOBAN
  );

  pyCollection
    .def(
      "dump",
      py::overload_cast<const path &>(&Collection::dump, py::const_),
      py::arg("dst").none(false)
    )
    .def(
      "dump",
      py::overload_cast<const string &>(&Collection::dump, py::const_),
      py::arg("dst").none(false)
    )
    .def(
      "dump",
      py::overload_cast<const Collection &, py::object &>(&stream_dump),
      py::arg("dst").none(false)
    );

  pyCollection.def("dumps", &Collection::dumps);
}

void stream_load(Collection &self, py::object &stream, Tessellation tessellation_hint) {
  // Assume stream is Python stream object (io.TextIOWrapper, io.StringIO, ...)
  // and read all lines from it into memory.
  //
  // This is quite inefficient, but only way to preserve Python Collection.load API
  //
  // Since collections are expected to be only few MiB in size, we don't care about
  // inefficiency here.
  string data;

  {
    stream.attr("seek")(0, 0);
    ostringstream conv;
    for (auto &line : stream) {
      if (py::isinstance<py::bytes>(line)) {
        conv << line.attr("decode")("utf-8");
      } else {
        conv << line;
      }
    }
    data = conv.str();
  }

  istringstream input(data);
  self.load(input);
}

void stream_dump(const Collection &self, py::object &stream) {
  string data;

  ostringstream conv;
  self.dump(conv);

  py::str stream_type_name = py::str(stream.get_type().attr("__name__"));

  if (
    stream_type_name.equal(py::str("BufferedWriter"))
    || stream_type_name.equal(py::str("BytesIO"))
    || stream_type_name.equal(py::str("FileIO"))
  ) {
    std::cout << py::str(conv.str()).attr("encode")("utf-8") << std::endl;
    stream.attr("write")(py::str(conv.str()).attr("encode")("utf-8"));
  } else {
    stream.attr("write")(conv.str());
  }
}
