# EDIT/RUN Mode System - Implementation Plan (Phase 8)

## Overview
Enhanced EDIT/RUN mode system incorporating the pyxdlg.py modal dialog capabilities for comprehensive device configuration and circuit construction management.

## Mode System Architecture

### 1. Mode Types (to be added to `config.py`)
```python
class SimulatorMode(Enum):
    EDIT = "EDIT"        # Circuit construction mode
    RUN = "RUN"          # Simulation execution mode
    DIALOG = "DIALOG"    # Modal dialog active (temporary)
```

### 2. EDIT Mode Features
- **Device Placement & Configuration**: Click-to-place with immediate configuration dialog
- **Circuit Construction**: Real-time visual feedback during construction
- **Device Properties**: ENTER key opens configuration dialog for selected device
- **Grid Operations**: Move, copy, delete operations with visual feedback
- **Preview System**: Enhanced placement preview with validation

### 3. RUN Mode Features  
- **Simulation Lock**: Device placement/editing disabled
- **Input Operation**: X devices (inputs) toggleable via click or Shift+1-4
- **Real-time Visualization**: Live power flow and device state display
- **Monitor Panel**: Enhanced device status with timing information

## Key Bindings & Interface

### Mode Control
- **TAB**: Toggle between EDIT ↔ RUN modes
- **ESC**: Exit dialog mode / Cancel current operation

### EDIT Mode Operations
- **1-7 keys**: Device palette selection
- **Mouse Click**: Device placement (opens config dialog if applicable)
- **ENTER**: Configure selected device (opens appropriate dialog)
- **DEL/BACKSPACE**: Delete device at cursor position
- **CTRL+C/V**: Copy/paste device configurations (future)

### RUN Mode Operations
- **Mouse Click**: Toggle X device states (inputs only)
- **Shift+1-4**: Toggle X001-X004 (legacy hotkeys)
- **SPACE**: Pause/resume simulation (future)

## Dialog System Integration

### Device Configuration Dialogs
1. **Device Address Dialog** (`dialogs/device_settings.json`)
   - Input validation for device address format
   - Type-specific validation (X001-X377, Y001-Y377, etc.)
   - Immediate address conflict checking

2. **Timer Configuration** (`dialogs/timer_settings.json`)
   - Preset time value input (seconds/milliseconds)
   - Timer type selection (TON, TOF, etc.)
   - Address and timing validation

3. **Counter Configuration** (`dialogs/counter_settings.json`)
   - Preset count value input
   - Count direction (UP/DOWN)
   - Reset conditions

### Dialog Workflow
```python
# Device placement workflow in EDIT mode
1. Select device from palette (1-7 keys)
2. Click grid position
3. Auto-open configuration dialog
4. Validate and apply settings
5. Place device with configured properties
```

## Visual Enhancements

### Mode Indicators
- **Top Bar Display**: Current mode (EDIT/RUN) with color coding
- **Status Line**: Mode-specific help text
- **Cursor Changes**: Different cursors for different modes

### EDIT Mode Visuals
- **Placement Grid**: Enhanced grid with snap indicators
- **Device Preview**: Real-time placement preview with validation
- **Configuration Indicators**: Visual hints for configurable devices
- **Wiring Assistant**: Connection path highlighting

### RUN Mode Visuals
- **Locked Indicators**: Visual indication of locked editing
- **Interactive Highlights**: Clickable input devices highlighted
- **Power Flow Animation**: Enhanced real-time power visualization
- **Status Dashboard**: Comprehensive device monitoring panel

## Implementation Plan

### Phase 8.1: Core Mode System
- [ ] Add `SimulatorMode` enum to `config.py`
- [ ] Implement mode state management in `main.py`
- [ ] Add TAB key mode switching
- [ ] Create mode-specific UI rendering
- [ ] Add mode indicator display in top bar

### Phase 8.2: EDIT Mode Enhancement
- [ ] Integrate pyxdlg.py dialog system into main.py
- [ ] Implement device configuration workflows
- [ ] Add enhanced placement preview system
- [ ] Create validation feedback system
- [ ] Add ENTER key device configuration trigger

### Phase 8.3: RUN Mode Features
- [ ] Implement editing lock system
- [ ] Add input device interaction in RUN mode
- [ ] Create enhanced monitoring dashboard
- [ ] Add simulation control features
- [ ] Implement mouse click input toggling

### Phase 8.4: UI Polish & Testing
- [ ] Mode transition animations
- [ ] Enhanced visual feedback
- [ ] Keyboard shortcut help system
- [ ] Error handling and user feedback
- [ ] Comprehensive testing of all modes

## Technical Integration Points

### Dialog System Usage
```python
from pyxdlg import PyxDialog, InputType

# Device address configuration
dialog = PyxDialog()
success, address = dialog.input_text_dialog(
    "Device Address", 
    "Enter device address:", 
    "X001", 
    InputType.DEVICE_ADDRESS
)
```

### Mode Management
```python
class PLCSimulator:
    def __init__(self):
        self.current_mode = SimulatorMode.EDIT
        self.dialog_system = PyxDialog()
        
    def handle_tab_key(self):
        if self.current_mode == SimulatorMode.EDIT:
            self.current_mode = SimulatorMode.RUN
        elif self.current_mode == SimulatorMode.RUN:
            self.current_mode = SimulatorMode.EDIT
```

### Device Configuration Integration
```python
def handle_device_placement(self, grid_x, grid_y, device_type):
    # Auto-open configuration dialog for configurable devices
    if device_type in [DeviceType.TIMER, DeviceType.COUNTER]:
        success, config = self.show_device_config_dialog(device_type)
        if success:
            self.place_configured_device(grid_x, grid_y, device_type, config)
    else:
        self.place_device(grid_x, grid_y, device_type)
```

## Benefits

### User Experience
- **Intuitive Workflow**: Clear separation between construction and testing
- **Immediate Feedback**: Real-time validation and visual guidance
- **Comprehensive Configuration**: Full device property management
- **Professional Interface**: Modal dialogs for complex settings

### Technical Advantages
- **Clean Architecture**: Clear mode separation prevents state conflicts
- **Extensible Design**: Easy addition of new device types and configurations
- **Robust Validation**: Type-safe input handling with immediate feedback
- **Maintainable Code**: Modular design with clear responsibilities

## Future Extensions

### Advanced EDIT Features
- **Circuit Templates**: Pre-built circuit patterns
- **Device Libraries**: Custom device definitions
- **Undo/Redo System**: Full operation history management
- **Circuit Validation**: Real-time error checking

### Enhanced RUN Features
- **Simulation Speed Control**: Variable execution speed
- **Breakpoint System**: Debug-style simulation control
- **Data Logging**: Historical value tracking
- **Performance Metrics**: Scan time monitoring

## Notes
- This plan leverages the existing pyxdlg.py dialog system (559 lines)
- All existing functionality will be preserved during implementation
- Mode system provides foundation for future advanced features
- Implementation follows existing modular architecture patterns