package mcdiamond.mixin;

import it.unimi.dsi.fastutil.ints.Int2ObjectMap;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(targets = "net.minecraft.class_3898", remap = false)
public interface ChunkStorageAccess {
    @Accessor(value = "field_18242", remap = false)
    Int2ObjectMap<?> mcdiamondTrackers();
}
