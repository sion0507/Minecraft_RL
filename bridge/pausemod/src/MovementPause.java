package mcdiamond.mixin;

import carpet.helpers.TickSpeed;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Keep connection/keepalive processing alive while rejecting frozen movement. */
@Mixin(targets = "net.minecraft.class_3244", remap = false)
public abstract class MovementPause {
    @Inject(method = {"method_12063", "method_12078"}, at = @At("HEAD"), cancellable = true, remap = false)
    private void freezeMovement(CallbackInfo callback) {
        if (TickSpeed.isPaused() && !TickSpeed.process_entities) callback.cancel();
    }
}
