# PLC Simulator Logic Refactoring Plan

This document outlines a refactoring plan for the Pyxel-based PLC simulator. The goal is to improve performance, enhance extensibility, and increase maintainability.

## 1. Performance Optimization: Introduce Incremental Updates

### Current Issue:
The `PLCController.scan_and_solve` method performs a full recalculation of the entire circuit's power state on every frame. This can lead to performance degradation in large or complex circuits.

### Proposed Solution:
Implement an event-driven, incremental update mechanism. The power-flow calculation should only be triggered when the circuit's state changes.

#### Implementation Steps:
1.  **Introduce a "dirty" flag:** Create a state manager (or use a flag in `PLCController`) like `circuit_state_changed = True`.
2.  **Trigger recalculation on events:** Set this flag to `True` only when a user action occurs that can affect the logic outcome. These actions include:
    *   Adding or removing a `LogicElement`.
    *   Toggling a switch's `is_on` state.
3.  **Conditional execution:** Modify the main application loop to call `scan_and_solve` only if `circuit_state_changed` is `True`.
4.  **Reset the flag:** After the calculation is complete, reset the flag to `False`.

### Benefit:
This change will significantly reduce CPU load, as calculations are performed only when necessary, rather than on every single frame.

## 2. Extensibility Improvement: Use Polymorphism for Device Logic

### Current Issue:
The `PLCController.trace_power` method likely contains conditional logic (e.g., `if/elif` statements) based on `LogicElement.type` strings. This makes adding new device types cumbersome and error-prone, as it requires modifying the central controller logic.

### Proposed Solution:
Delegate the power-flow logic to the `LogicElement` objects themselves by leveraging polymorphism.

#### Implementation Steps:
1.  **Define an abstract method in the base class:** In the `LogicElement` base class, define a new abstract method:
    ```python
    from abc import ABC, abstractmethod

    class LogicElement(ABC):
        # ... existing attributes ...

        @abstractmethod
        def can_power_pass_through(self, input_direction: tuple[int, int]) -> bool:
            """Determines if power can flow through this element."""
            pass
    ```
2.  **Implement the method in subclasses:** Each concrete subclass of `LogicElement` will provide its own implementation of this method.
    *   **`Line`:** Will always return `True`.
    *   **`Switch`:** Will return `True` if `self.is_on` is `True` (for a normally-open switch), and `False` otherwise.
    *   **`Coil`:** Will always return `False` as it's a terminal element.
    *   **`NC_Switch` (future):** Will return `True` if `self.is_on` is `False`.
3.  **Refactor the controller:** The `PLCController.trace_power` method will no longer check the element type. It will simply call the `can_power_pass_through()` method on the element object.

    **Conceptual Change in `trace_power`:**
    ```python
    # Before
    if element.type == 'switch' and not element.is_on:
        # stop
    
    # After
    if not element.can_power_pass_through(direction):
        # stop
    ```

### Benefit:
This decouples the controller from the specific logic of each device. New device types can be added simply by creating a new subclass, with no modifications needed to `PLCController`. This greatly improves modularity and extensibility.

## 3. State Management Centralization

### Current Issue:
The state of a `LogicElement` (e.g., `is_on`, `is_powered`) might be modified by different parts of the system (e.g., `InputHandler`, `PLCController`). This distribution of state-mutating logic can lead to inconsistencies and bugs.

### Proposed Solution:
Centralize all state modifications through a single, authoritative manager, such as an enhanced `GridManager` or a new `CircuitStateManager`.

#### Implementation Steps:
1.  **Define a clear API for state changes:** The state manager will expose high-level methods for all possible state mutations.
    *   `state_manager.toggle_switch(coordinates)`
    *   `state_manager.set_element_powered(coordinates, is_powered)`
    *   `state_manager.add_element(element, coordinates)`
2.  **Refactor other components:** All other components must use this new API instead of directly modifying an element's state.
    *   `InputHandler`: On a click, it calls `state_manager.toggle_switch(coord)`.
    *   `PLCController`: After calculation, it calls `state_manager.set_element_powered(coord, True)`.
3.  **Encapsulate state:** Make the state attributes of `LogicElement` "private" (e.g., using a `_` prefix) to discourage direct external modification.

### Benefit:
This creates a single source of truth for the circuit's state, making the application's data flow predictable, easier to debug, and more robust against bugs.
