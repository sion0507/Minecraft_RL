package mcdiamond.mixin;

import net.minecraft.class_2168;
import net.minecraft.server.MinecraftServer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Only the administrator step bypasses the console's end-of-tick command queue. */
@Mixin(targets = "net.minecraft.class_3176", remap = false)
public abstract class AdminStep {
    @Inject(method = "method_13947", at = @At("HEAD"), cancellable = true, remap = false)
    private void scheduleStep(String command, class_2168 source, CallbackInfo callback) {
        if (!command.startsWith("mcdiamond_step ")) return;
        MinecraftServer server = (MinecraftServer) (Object) this;
        // Use the server executor, never change TickSpeed on the stdin thread.
        server.execute(() -> server.method_3734().method_9249(source, command));
        callback.cancel();
    }
}
