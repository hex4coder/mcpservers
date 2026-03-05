{
  description = "A development environment for a Mikrotik MCP server in Python";

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
          ];

          shellHook = ''
            echo "Mikrotik MCP Python Development Environment"
            echo "Python version: $(python --version)"
            
            if [ ! -d ".venv" ]; then
              uv venv
            fi
            source .venv/bin/activate
            
            # Install mcp sdk and routeros-api
            uv add "mcp[cli]" routeros-api python-dotenv
          '';
        };
      }
    );
}
