package mcdiamond.mixin;

import java.nio.charset.StandardCharsets;
import mcdiamond.PauseExtension;
import net.minecraft.class_2817;
import net.minecraft.class_2960;
import net.minecraft.class_3222;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

@Mixin(targets = "net.minecraft.class_3244", remap = false)
public abstract class ClientStep {
    @Shadow(remap = false)
    public class_3222 field_14140;

    @Inject(method = "method_12075", at = @At("HEAD"), cancellable = true, remap = false)
    private void acknowledgeInput(class_2817 packet, CallbackInfo callback) {
        StepPayloadAccess payload = (StepPayloadAccess) packet;
        if (!new class_2960("mcdiamond:step_ready").equals(payload.mcdiamondChannel())) return;
        if (payload.mcdiamondData().readableBytes() == 36) {
            String nonce = payload.mcdiamondData().toString(StandardCharsets.UTF_8);
            // Same connection, same executor: earlier movement handlers finish first.
            field_14140.field_13995.execute(() -> PauseExtension.confirmInput(field_14140, nonce));
        }
        callback.cancel();
    }
}
