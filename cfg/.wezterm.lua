local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.enable_kitty_keyboard = true

-- 默认窗口大小（列数、行数）
config.initial_cols = 120
config.initial_rows = 30

wezterm.on('gui-startup', function(cmd)
  local tab, pane, window = mux.spawn_window({
    -- 默认窗口位置（像素）
    position = { x = 10, y = 10 },
  })
end)

return config
