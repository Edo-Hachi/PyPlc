# Project: Vertical Wiring Architecture Refactoring

## 1. Goal

The primary goal is to refactor the vertical wiring system by replacing the complex and non-intuitive `LINK_TO_UP` and `LINK_FROM_DOWN` devices with a simpler, more intuitive "BRANCH + VIRT" model. This will align the simulator's behavior more closely with real-world PLCs, simplify implementation, and improve scalability.

## 2. Problem Statement

The current architecture suffers from several issues:
- **Conceptual Complexity**: The `LINK_TO_UP` and `LINK_FROM_DOWN` concepts are artificial, creating a steep learning curve and making circuit design non-intuitive.
- **Implementation Discrepancy**: There is a mismatch between the design documentation and the actual implementation, leading to bugs where direct connections do not work as expected.
- **Lack of Scalability**: The current system makes it difficult to create and manage complex parallel circuits that span multiple rows.

## 3. Proposed Architecture: "BRANCH + VIRT" Model

We will introduce two new (or repurposed) device concepts:

- **`BRANCH_POINT`**: A T-junction device that receives power from one connection (typically 'left') and distributes it to all other connected directions ('right', 'up', 'down'). This single device handles all branching and merging logic.
- **`LINK_VIRT`**: A simple vertical wire that transmits power between its 'up' and 'down' connections.

### Example Circuit:

```
Row 1: ---[CONTACT_A]---[BRANCH_POINT]---[CONTACT_B]---(COIL)
Row 2:                     |
Row 3:                 [LINK_VIRT]
Row 4:                     |
Row 5: ---[CONTACT_C]---[BRANCH_POINT]
```

## 4. Refactoring Plan (Phased Approach)

### Phase 1: Preparation and New Concept Introduction

**Task**: Define the `BRANCH_POINT` device, its palette entry, and its visual sprite.
**Success Criterion**: The `BRANCH_POINT` device can be selected from the palette and placed on the grid.

1.  **Modify `config.py`**:
    - Add `BRANCH_POINT` to the `DeviceType` Enum.
    - Deprecate (comment out or mark for removal) `LINK_TO_UP` and `LINK_FROM_DOWN`.
    - Update `DEVICE_PALETTE_DEFINITIONS` to replace an existing link device with `BRANCH_POINT`.

    ```python
    # In config.py
    class DeviceType(Enum):
        # ... existing devices
        BRANCH_POINT = "BRANCH_POINT"
        # LINK_TO_UP = "LINK_TO_UP" # To be removed
        # LINK_FROM_DOWN = "LINK_FROM_DOWN" # To be removed
    
    DEVICE_PALETTE_DEFINITIONS = {
        # ...
        '9': {'type': DeviceType.BRANCH_POINT, 'name': 'Branch', 'key': '9'},
        # ...
    }
    ```

2.  **Modify `sprites.json`**:
    - Add a new entry for `BRANCH_POINT` with "ON" and "OFF" sprite coordinates.

3.  **Modify `my_resource.pyxres` (User/Manual Task)**:
    - Create and add a T-shaped sprite for `BRANCH_POINT` in both OFF and ON states.

### Phase 2: Core Logic Refactoring

**Task**: Rewrite the power tracing algorithm in `circuit_analyzer.py` to use the new model.
**Success Criterion**: The power flow correctly traces through `BRANCH_POINT` and `LINK_VIRT` devices.

1.  **Modify `core/circuit_analyzer.py`**:
    - In the `_trace_power_flow` method (or equivalent), add logic to handle `BRANCH_POINT`.
    - When the trace encounters an energized `BRANCH_POINT`, it should recursively call `_trace_power_flow` for all connected neighbors (`up`, `down`, `right`) that haven't been visited.
    - Ensure the logic for `LINK_VIRT` simply passes power up and down.
    - Remove or disable the old logic for `LINK_TO_UP` and `LINK_FROM_DOWN`.

    ```python
    # In core/circuit_analyzer.py, inside _trace_power_flow
    
    # ...
    # Mark current_device as visited
    
    device_type = current_device.device_type
    
    if not self._is_conductive(current_device):
        return

    current_device.is_energized = True

    if device_type == DeviceType.BRANCH_POINT:
        # Trace to all connected directions
        for direction in ['right', 'up', 'down']:
            next_pos = current_device.connections.get(direction)
            if next_pos and next_pos not in visited:
                self._trace_power_flow(next_pos, visited)
    
    elif device_type == DeviceType.LINK_VIRT:
        # Trace up and down
        for direction in ['up', 'down']:
             next_pos = current_device.connections.get(direction)
             if next_pos and next_pos not in visited:
                self._trace_power_flow(next_pos, visited)

    else: # For standard devices
        # Trace to the right
        next_pos = current_device.connections.get('right')
        if next_pos and next_pos not in visited:
            self._trace_power_flow(next_pos, visited)
    ```

### Phase 3: Testing and Verification

**Task**: Update all test cases to use the new architecture and verify that all circuit types function correctly.
**Success Criterion**: Self-holding circuits, parallel circuits, and series circuits work as expected with the new model.

1.  **Rewrite Test CSVs**:
    - `test_link_direct.csv`
    - `test_link_virt_1row.csv`
    - `test_link_virt_2row.csv`
    - Modify these files to build parallel circuits using `BRANCH_POINT` and `LINK_VIRT`.

2.  **Perform Manual Testing**:
    - Load the new test files.
    - Build a standard self-holding circuit using the new components.
    - Build a multi-row parallel circuit.
    - Verify that power flows correctly in all scenarios in RUN mode.

### Phase 4: Cleanup

**Task**: Remove all remnants of the old `LINK_TO_UP`/`LINK_FROM_DOWN` system.
**Success Criterion**: The codebase is clean, with no dead code related to the old architecture.

1.  **Finalize `config.py`**:
    - Delete the `DeviceType` enums for `LINK_TO_UP` and `LINK_FROM_DOWN`.

2.  **Finalize `core/circuit_analyzer.py`**:
    - Remove any remaining code blocks related to the old link devices.

3.  **Finalize `sprites.json`**:
    - Remove the sprite definitions for the old link devices.

4.  **Update Documentation**:
    - Review `_Common_Report.md` and other documents to reflect the new, simpler architecture.
