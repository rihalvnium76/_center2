# If not running interactively, don't do anything
[[ $- != *i* ]] && return

_setup_git_prompt() {
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
_setup_git_prompt
unset -f _setup_git_prompt

_set_ps1() {
    # MUST be at the start
    local exit_code=$?

    local exit_color=""
    (( exit_code )) && exit_color="\[\e[91m\]"

    local ip=$(ip route | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="src") {print $(i+1); exit}}')
    ip=${ip:-"-"}

    local git_ps="$(__git_ps1 '%s' 2>/dev/null)"
    [[ -n $git_ps ]] && git_ps=" \[\e[36m\](${git_ps})\[\e[97m\]"

    PS1="\n\[\e[97m\][\[\e[32m\]\w\[\e[97m\] \t \u ${ip} ${exit_color}${exit_code}\[\e[97m\]${git_ps}]\n\$\[\e[0m\] "

    if [[ -v TMUX ]]; then
        tmux set-environment LOCAL_IP "${ip}"
    fi

   return $exit_code
}
PROMPT_COMMAND='_set_ps1'

alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias ll='ls -lA --time-style iso'
alias which='command -v'
alias py='python3'

if [ -t 0 ]; then
    export GPG_TTY=$(tty)
fi

# (Optional) Android storage directory
if [[ ! -v _INIT_BASE_DIR ]]; then
    cd /sdcard
    export _INIT_BASE_DIR=1
fi

if [[ ! -v NO_TMUX && $- == *i* && -v SSH_CONNECTION ]] && command -v tmux >/dev/null 2>&1; then
    if [[ ! -v TMUX ]]; then
        exec tmux new-session -A -s 0
    else
        alias rescue="exec tmux detach -E 'NO_TMUX=1 exec bash'"
    fi  
fi
