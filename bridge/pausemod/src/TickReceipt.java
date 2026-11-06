package mcdiamond.mixin;

import java.util.function.BooleanSupplier;
import net.minecraft.server.MinecraftServer;
import mcdiamond.PauseExtension;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Fence after world, network and player updates, never at tick start. */
@Mixin(value = MinecraftServer.class, remap = false)
public abstract class TickReceipt {
    @Inject(method = "method_3748", at = @At("TAIL"), remap = false)
    private void completedTick(BooleanSupplier shouldKeepTicking, CallbackInfo callback) {
        PauseExtension.completedTick((MinecraftServer) (Object) this);
    }
}
