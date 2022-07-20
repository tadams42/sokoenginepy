#include <CLI/CLI.hpp>
#include <sokoengine.hpp>

using namespace sokoengine;
namespace fs = std::filesystem;

using std::string;

struct IsTessellationValidator : public CLI::Validator {
  IsTessellationValidator() {
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
};

static const IsTessellationValidator IsTessellation;

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

int main(int argc, char **argv) {
  CLI::App app{"Parsing of \"Common Skins Format\" Sokoban images"};

  fs::path skin_file;
  app.add_option("skin", skin_file, "Path to skin image (.bmp or .png).")
    ->required()
    ->check(CLI::ExistingFile);

  string tessellation_s;
  app
    .add_option(
      "-t, --tessellation",
      tessellation_s,
      "Tessellation for given skin: \"sokoban\", \"hexoban\", \"trioban\" or "
      "\"octoban\"."
    )
    ->check(IsTessellation)
    ->default_val("sokoban");

  fs::path output_dir;
  app
    .add_option(
      "-o, --output_dir",
      output_dir,
      "Output directory. Will be created if it doesn't exist."
    )
    ->default_val("./skin_tiles/");

  CLI11_PARSE(app, argc, argv);

  Tessellation t = from_str(tessellation_s);

  fs::path tmp = skin_file.filename();
  tmp.replace_extension("");
  output_dir = output_dir / tmp;
  fs::create_directories(output_dir);

  Skin skin(from_str(tessellation_s), skin_file.string());
  skin.dump_tiles(output_dir.string());

  return 0;
}
