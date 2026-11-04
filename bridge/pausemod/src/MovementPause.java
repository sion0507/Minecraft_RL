package mcdiamond.mixin;

import carpet.helpers.TickSpeed;
import net.minecraft.class_2828;
import net.minecraft.class_243;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Keep frozen positions unchanged; deliver the latest motion on an active tick. */
@Mixin(targets = "net.minecraft.class_3244", remap = false)
public abstract class MovementPause {
    private class_2828 mcdiamondPosition;
    private class_2828 mcdiamondLook;
    private boolean mcdiamondReplay;

    @Shadow(remap = false)
    private class_243 field_14119;

    @Shadow(remap = false)
    public abstract void method_12063(class_2828 packet);

    // Run after vanilla's server-thread handoff, never on the Netty reader thread.
    @Inject(method = "method_12063", at = @At(value = "INVOKE",
        target = "Lnet/minecraft/class_2600;method_11073(Lnet/minecraft/class_2596;Lnet/minecraft/class_2547;Lnet/minecraft/class_3218;)V",
        shift = At.Shift.AFTER), cancellable = true, remap = false)
    private void queueMovement(class_2828 packet, CallbackInfo callback) {
        if (mcdiamondReplay) return;
        if (TickSpeed.isPaused() && !TickSpeed.process_entities) {
            if (field_14119 == null) {
                if (!Double.isNaN(packet.method_12269(Double.NaN))) {
                    mcdiamondPosition = packet;
                    if (!Float.isNaN(packet.method_12271(Float.NaN))) mcdiamondLook = null;
                } else if (!Float.isNaN(packet.method_12271(Float.NaN))) mcdiamondLook = packet;
            }
            callback.cancel();
        } else applyMovement(callback);
    }

    @Inject(method = "method_18784", at = @At("HEAD"), remap = false)
    private void applyMovement(CallbackInfo callback) {
        if (TickSpeed.isPaused() && !TickSpeed.process_entities) return;
        class_2828 position = mcdiamondPosition;
        class_2828 look = mcdiamondLook;
        mcdiamondPosition = mcdiamondLook = null;
        mcdiamondReplay = true;
        try {
            if (position != null) method_12063(position);
            if (look != null) method_12063(look);
        } finally { mcdiamondReplay = false; }
    }

    @Inject(method = "method_14360", at = @At("HEAD"), remap = false)
    private void clearTeleport(CallbackInfo callback) {
        mcdiamondPosition = mcdiamondLook = null;
    }

    @Inject(method = "method_12078", at = @At("HEAD"), cancellable = true, remap = false)
    private void freezeVehicle(CallbackInfo callback) {
        if (TickSpeed.isPaused() && !TickSpeed.process_entities) callback.cancel();
    }
}
