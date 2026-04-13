_set_ps1() {
    # MUST be at the start
    local exit_code=$?

    local exit_color=""
    if [ $exit_code -ne 0 ]; then exit_color="\[\e[91m\]"; fi

    local ip=$(ip route | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="src") {print $(i+1); exit}}')
    ip=${ip:-"-"}

    PS1="\n\[\e[97m\][\[\e[32m\]\w\[\e[97m\] \t \u ${ip} ${exit_color}${exit_code}\[\e[97m\]]\n\$\[\e[0m\] "

    if [ -n "$TMUX" ]; then
        tmux set-environment LOCAL_IP "${ip}"
    fi

   return $exit_code
}
PROMPT_COMMAND='_set_ps1'

alias ll='ls -lA --time-style iso'
alias which='command -v'
alias py='python3'

if [ -t 0 ]; then
    export GPG_TTY=$(tty)
fi

# (Optional) Android storage directory
if [ -z "$_INIT_BASE_DIR" ]; then
    cd /sdcard
    export _INIT_BASE_DIR=1
fi

if [ -z "$NO_TMUX" ] && [[ $- == *i* ]] && [ -n "$SSH_CONNECTION" ] && command -v tmux >/dev/null 2>&1; then
    if [ -z "$TMUX" ]; then
        exec tmux new-session -A -s 0
    else
        alias rescue="exec tmux detach -E 'NO_TMUX=1 exec bash'"
    fi  
fi
