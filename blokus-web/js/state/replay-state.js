import { StateMachine } from '../utils/state-machine.js';

/**
 * Replay playback states
 */
export const ReplayState = {
    IDLE: 'idle',           // Reset or beginning
    PLAYING: 'playing',     // Animating through moves
    PAUSED: 'paused',       // Stopped mid-replay
    FINISHED: 'finished'    // Reached the end of move history
};

/**
 * Valid transitions for replay playback
 */
const REPLAY_TRANSITIONS = {
    [ReplayState.IDLE]: [ReplayState.PLAYING, ReplayState.PAUSED, ReplayState.IDLE],
    [ReplayState.PLAYING]: [ReplayState.PAUSED, ReplayState.FINISHED, ReplayState.IDLE],
    [ReplayState.PAUSED]: [ReplayState.PLAYING, ReplayState.IDLE, ReplayState.FINISHED, ReplayState.PAUSED],
    [ReplayState.FINISHED]: [ReplayState.IDLE, ReplayState.PLAYING, ReplayState.PAUSED, ReplayState.FINISHED]
};

/**
 * State Machine for Replay playback
 */
export class ReplayStateMachine extends StateMachine {
    constructor() {
        super(ReplayState.IDLE, REPLAY_TRANSITIONS);
    }

    play() { if (this.canTransitionTo(ReplayState.PLAYING)) this.transitionTo(ReplayState.PLAYING); }
    pause() { if (this.canTransitionTo(ReplayState.PAUSED)) this.transitionTo(ReplayState.PAUSED); }
    finish() { if (this.canTransitionTo(ReplayState.FINISHED)) this.transitionTo(ReplayState.FINISHED); }
    reset() { if (this.canTransitionTo(ReplayState.IDLE)) this.transitionTo(ReplayState.IDLE); }
}
