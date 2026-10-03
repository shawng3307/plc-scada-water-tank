PROGRAM tank_simulation
  VAR
  END_VAR
  VAR_EXTERNAL
    tank_level : INT;
    pump_on : BOOL;
    timer_pulse : BOOL;
  END_VAR

IF timer_pulse then
    if pump_on then
        tank_level := tank_level + 2;
    else
        tank_level := tank_level - 1;
    end_if

    if tank_level > 100 then
        tank_level := 100;
    end_if;

    if tank_level < 0 then
        tank_level := 0;
    end_if;
end_if

END_PROGRAM