local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.enable_kitty_keyboard = true

-- 设置默认窗口大小为 120 列 × 30 行
config.initial_cols = 120
config.initial_rows = 30

return config
