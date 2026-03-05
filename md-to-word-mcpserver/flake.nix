{
  description = "A development environment for an MCP server in Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            uv
            pandoc
            texlive.combined.scheme-small
          ];

          shellHook = ''
            echo "MCP Python Development Environment (Markdown to Word & PDF)"
            echo "Python version: $(python --version)"
            echo "Pandoc version: $(pandoc --version)"
            echo "TeX Live (pdfLaTeX) available"
            
            if [ ! -d ".venv" ]; then
              uv venv
            fi
            source .venv/bin/activate
            
            uv add "mcp[cli]" pypandoc
          '';
        };
      }
    );
}
