# nixos-grapher

a little tool, that generates a block diagram with the build files as entries, powered by the kroki-api.

if you are writing your configuration in ~/.config/nixos this program generates a clearer overview, of what you have imported and what not. 
## example

![nixos-imports](./nix-imports.png)

## known issues 

- [ ] does not yet work with files declared via let-in e.g. : 
```
let
base = import ./base.nix pkgs;
in
...
```

- [ ] does not yet add grandchildren of inactive imported files to the inactive list
- [ ] works with clear text post not encoded get-request 

