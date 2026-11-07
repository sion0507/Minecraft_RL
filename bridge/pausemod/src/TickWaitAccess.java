package mcdiamond.mixin;

import net.minecraft.server.MinecraftServer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

/** The two timestamps MinecraftServer.method_3866 compares while waiting for its next tick. */
@Mixin(value = MinecraftServer.class, remap = false)
public interface TickWaitAccess {
    @Accessor(value = "field_4571", remap = false)
    void mcdiamondTickReference(long milliseconds);

    @Accessor(value = "field_19248", remap = false)
    void mcdiamondNextTick(long milliseconds);
}
