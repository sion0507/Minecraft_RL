package mcdiamond.mixin;

import carpet.helpers.TickSpeed;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Carpet 1.16.5 freezes world ticks but deliberately continues player simulation. */
@Mixin(targets = "net.minecraft.class_3222", remap = false)
public abstract class PlayerPause {
    @Inject(method = {"method_5773", "method_14226"}, at = @At("HEAD"), cancellable = true, remap = false)
    private void freezePlayer(CallbackInfo callback) {
        if (TickSpeed.isPaused() && !TickSpeed.process_entities) callback.cancel();
    }
}
