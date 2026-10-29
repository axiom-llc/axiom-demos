# AXIOM Blender

Deterministic Blender scene automation driven by declarative JSON configuration.

`axiom-blender` separates art direction from scene execution: routine scene changes live in JSON, while `scene.py` provides the bounded Blender implementation.

## Requirements

- Blender 5.2 LTS
- Python runtime bundled with Blender

No third-party Python packages are required.

## Quick start

Copy the example configuration:

```bash
cp scene.example.json scene.json
```

Render from a clean Blender state:

```bash
blender --factory-startup -b -P scene.py
```

The script writes:

- `render.png`
- `scene.blend`

Both are generated outputs and are ignored by Git.

## Configuration

`scene.example.json` controls:

- orthographic camera position and scale;
- cube position, size, base color, metallic value, and roughness;
- world color and strength;
- area-light positions, energies, and sizes;
- optional ground material color and roughness.

The checked-in `examples/render.png` is a reference render produced from the example configuration.

## Compatibility

The current implementation is validated against Blender 5.2.1 LTS.

Blender 5.2 exposes material and world node trees directly, so the script intentionally does not assign the deprecated `use_nodes = True` compatibility flag.

## Validation

Run:

```bash
make test
```

The test uses a temporary directory, executes Blender headlessly with `--factory-startup`, verifies that both generated outputs exist, and rejects relevant Blender errors or `use_nodes` deprecation warnings.

## Scope

Declarative scene configuration drives deterministic rendering, camera, lighting and material automation. Schema evolution preserves backward compatibility.

## License

MIT
