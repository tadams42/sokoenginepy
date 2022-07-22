#include <CLI/CLI.hpp>
#include <iostream>
#include <sokoengine.hpp>

using namespace sokoengine;
namespace fs = std::filesystem;

using std::cerr;
using std::endl;
using std::string;

struct IsTessellationValidator : public CLI::Validator {
  IsTessellationValidator();
};

Tessellation from_str(const string &str);
void         dump_tiles(
          const Skin &skin, const fs::path &skin_file, const fs::path &output_dir
        );
void render_board(
  const Skin     &skin,
  const fs::path &collection_path,
  uint16_t        puzzle_index,
  const fs::path &rendered_board_path
);

static const IsTessellationValidator IsTessellation;

int main(int argc, char **argv) {
  CLI::App app{"Parsing of \"Common Skins Format\" Sokoban images"};
  app.require_subcommand(/* min */ 1, /* max */ 1);

  fs::path skin_file;
  app.add_option("-s, --skin", skin_file, "Path to skin image (.bmp or .png).")
    ->required()
    ->check(CLI::ExistingFile);

  CLI::App *dump_tiles_sub = app.add_subcommand(
    "dump_tiles", "Saves individual skin tile images into some directory."
  );
  fs::path output_dir;
  dump_tiles_sub
    ->add_option(
      "-d, --output-dir",
      output_dir,
      "Output directory. Will be created if it doesn't exist."
    )
    ->default_val("./skin_tiles/");
  string tessellation_s;
  dump_tiles_sub
    ->add_option(
      "-t, --tessellation",
      tessellation_s,
      "Tessellation for given skin: \"sokoban\", \"hexoban\", \"trioban\" or "
      "\"octoban\"."
    )
    ->check(IsTessellation)
    ->default_val("sokoban");

  CLI::App *render_board_sub = app.add_subcommand(
    "render_board", "Uses skin to render example board and saves resulting board image."
  );
  fs::path collection_path;
  render_board_sub
    ->add_option(
      "-c, --sok-collection", collection_path, ".sok file with at least one puzzle"
    )
    ->required()
    ->check(CLI::ExistingFile);

  uint16_t puzzle_index;
  render_board_sub
    ->add_option(
      "-p, --puzzle", puzzle_index, "Index of puzzle in --sok--collection (zero based)"
    )
    ->default_val("0");

  fs::path rendered_board_path;
  render_board_sub
    ->add_option(
      "-o, --output_file", rendered_board_path, "File path for rendered board image."
    )
    ->default_val("./board.png");

  CLI11_PARSE(app, argc, argv);

  Tessellation t = from_str(tessellation_s);
  Skin         skin(from_str(tessellation_s), skin_file.string());

  if (dump_tiles_sub->parsed()) {
    dump_tiles(skin, skin_file, output_dir);
  } else if (render_board_sub->parsed()) {
    render_board(skin, collection_path, puzzle_index, rendered_board_path);
  }

  return 0;
}

void dump_tiles(
  const Skin &skin, const fs::path &skin_file, const fs::path &output_dir
) {
  fs::path tmp = skin_file.filename();
  tmp.replace_extension("");
  fs::path output_dir2 = output_dir / tmp;
  fs::create_directories(output_dir2);
  skin.dump_tiles(output_dir2.string());
}

void render_board(
  const Skin     &skin,
  const fs::path &collection_path,
  uint16_t        puzzle_index,
  const fs::path &rendered_board_path
) {
  Collection collection;
  collection.load(collection_path);
  if (puzzle_index >= collection.puzzles().size()) {
    cerr << "No such puzzle ( " << puzzle_index << ") in collection " << collection_path
         << "!" << endl;
    return;
  }
  const Puzzle puzzle      = collection.puzzles()[puzzle_index];
  Image        board_image = skin.render_board(puzzle);
  board_image.save(rendered_board_path.string());
}

Tessellation from_str(const string &str) {
  if (CLI::detail::to_lower(str) == "sokoban")
    return Tessellation::SOKOBAN;
  if (CLI::detail::to_lower(str) == "trioban")
    return Tessellation::TRIOBAN;
  if (CLI::detail::to_lower(str) == "hexoban")
    return Tessellation::HEXOBAN;
  if (CLI::detail::to_lower(str) == "octoban")
    return Tessellation::OCTOBAN;
  return Tessellation::SOKOBAN;
}

IsTessellationValidator::IsTessellationValidator() {
  name_ = "TESSELLATION";
  func_ = [](const string &str) {
    if (
        CLI::detail::to_lower(str) != "sokoban"
        && CLI::detail::to_lower(str) != "trioban"
        && CLI::detail::to_lower(str) != "hexoban"
        && CLI::detail::to_lower(str) != "octoban"
      )
      return string(
        "Tessellation must be one of: \"sokoban\", \"hexoban\", \"trioban\" or "
        "\"octoban\"."
      );
    else
      return string();
  };
}
