package mcdiamond.mixin;

import net.minecraft.class_3231;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(targets = "net.minecraft.class_3898$class_3208", remap = false)
public interface EntityTrackerAccess {
    @Accessor(value = "field_18246", remap = false)
    class_3231 mcdiamondEntry();
}
