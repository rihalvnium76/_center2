# If not running interactively, don't do anything
[[ $- != *i* ]] && return

export LANG=zh_CN.UTF-8
export LANGUAGE=zh_CN:zh

shrc_setup_git_prompt() {
    local git_prompt_file="$HOME/.git-prompt.sh"

    if [[ ! -f $git_prompt_file ]]; then
        echo "[I $(date +'%H:%M:%S') bashrc] Downloading official git-prompt.sh ..."
        curl -fsSL --max-time 10 -o "$git_prompt_file" "https://raw.githubusercontent.com/git/git/master/contrib/completion/git-prompt.sh" || rm -f "$git_prompt_file"
    fi

    if [[ -f $git_prompt_file ]]; then
        export GIT_PS1_SHOWCOLORHINTS=""

        export GIT_PS1_SHOWDIRTYSTATE=1
        export GIT_PS1_SHOWSTASHSTATE=1
        export GIT_PS1_SHOWUNTRACKEDFILES=1
        export GIT_PS1_SHOWUPSTREAM="auto verbose"
        export GIT_PS1_SHOWCONFLICTSTATE="yes"
        export GIT_PS1_HIDE_IF_PWD_IGNORED=1

        . "$git_prompt_file"
    fi
}
shrc_setup_git_prompt
unset -f shrc_setup_git_prompt

shrc_set_ps1() {
    # MUST be at the start
    local raw_exit_code=$?

    local end_time=$EPOCHREALTIME
    local start_time=$shrc_cmd_start_time
    unset shrc_cmd_start_time
    local elapsed_time=""
    if [[ -n $start_time ]]; then
        elapsed_time=$(( ${end_time/.} - ${start_time/.} ))
        if (( elapsed_time >= 10000 )); then
            local half_even=$(( (elapsed_time + 4999 + elapsed_time / 10000 % 2) / 10000 ))
            printf -v elapsed_time " %d.%02ds" "$(( half_even / 100 ))" "$(( half_even % 100 ))"
        else
            elapsed_time=""
        fi
    fi

    local exit_code=""
    (( raw_exit_code )) && exit_code=" \[\e[91m\]${raw_exit_code}\[\e[97m\]"

    local ip=$(ip route | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="src") {print $(i+1); exit}}')
    # ip=" ${ip:--}"
    if [[ -n $ip ]]; then
        [[ -v TMUX ]] && tmux set-environment LOCAL_IP "${ip}"

        ip=" ${ip}"
    fi

    local git_ps="$(__git_ps1 '%s' 2>/dev/null)"
    [[ -n $git_ps ]] && git_ps=" \[\e[36m\](${git_ps})\[\e[97m\]"

    PS1="\n\[\e[97m\][\[\e[32m\]\w\[\e[97m\] \t \u${ip}${exit_code}${elapsed_time}${git_ps}]\n\$\[\e[0m\] "

    return $raw_exit_code
}
PROMPT_COMMAND='shrc_set_ps1'

alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias ll='ls -lAh --time-style iso'
alias which='command -v'
alias py='python3'

if [ -t 0 ]; then
    export GPG_TTY=$(tty)
fi

if [[ ! -v SHRC_NO_TMUX && $- == *i* && -v SSH_CONNECTION ]] && command -v tmux >/dev/null 2>&1; then
    if [[ ! -v TMUX ]]; then
        exec tmux new-session -A -s ${SHRC_TMUX_SES:-0}
    else
        alias rescue="exec tmux detach -E 'SHRC_NO_TMUX=1 exec bash'"
    fi
fi

shrc_set_cmd_start_time() {
    local exit_code=$?
    local cmd
    for cmd in "${PROMPT_COMMAND[@]}"; do
        [[ "$BASH_COMMAND" == "$cmd" ]] && return $exit_code
    done
    shrc_cmd_start_time=$EPOCHREALTIME
    return $exit_code
}
trap 'shrc_set_cmd_start_time' DEBUG
